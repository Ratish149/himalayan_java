import logging

import firebase_admin
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from firebase_admin import credentials, messaging

from account.models import CustomUser
from notifications.models import Notification, UserDevice
from notifications.tracking import is_user_online

logger = logging.getLogger("notifications")

# Initialize Firebase Admin SDK (do this once)
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        logger.info("✓ Firebase Admin SDK initialized")
except Exception as e:
    logger.error(f"✗ Firebase initialization failed: {e}")

# Track online users
online_users = set()


def user_connected(user_id):
    """Mark user as online when WebSocket connects"""
    online_users.add(user_id)
    logger.info(f"✓ User {user_id} is now ONLINE")


def user_disconnected(user_id):
    """Mark user as offline when WebSocket disconnects"""
    online_users.discard(user_id)
    logger.info(f"✓ User {user_id} is now OFFLINE")


def send_fcm_notification(
    device_tokens, title="New Notification", message="", data=None
):
    """
    Send FCM push notification using Firebase Admin SDK

    Args:
        device_tokens: List of FCM device tokens
        title: Notification title
        message: Notification message
        data: Extra data dictionary (optional)

    Returns:
        dict: Result with success/failure counts
    """
    if not device_tokens:
        return {"success": 0, "failure": 0}

    success_count = 0
    failure_count = 0
    invalid_tokens = []

    # Prepare notification data
    notification_data = data or {}
    notification_data = {k: str(v) for k, v in notification_data.items()}

    for token in device_tokens:
        try:
            # Create FCM message
            fcm_message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=message,
                ),
                data=notification_data,
                token=token,
                # Android specific config
                android=messaging.AndroidConfig(
                    priority="high",
                    notification=messaging.AndroidNotification(
                        sound="default",
                        channel_id="default",
                    ),
                ),
                # iOS specific config
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound="default",
                            badge=1,
                        ),
                    ),
                ),
            )

            # Send the message
            response = messaging.send(fcm_message)
            success_count += 1
            logger.info(f"✓ FCM sent to token {token[:20]}...: {response}")

        except messaging.UnregisteredError:
            # Token is invalid/expired
            logger.warning(f"✗ Invalid token: {token[:20]}...")
            invalid_tokens.append(token)
            failure_count += 1

        except Exception as e:
            logger.error(f"✗ FCM send failed for token {token[:20]}...: {e}")
            failure_count += 1

    # Clean up invalid tokens from database
    if invalid_tokens:
        deleted = UserDevice.objects.filter(device_token__in=invalid_tokens).delete()[0]
        logger.info(f"🗑️  Removed {deleted} invalid device tokens")

    return {
        "success": success_count,
        "failure": failure_count,
        "invalid_tokens_removed": len(invalid_tokens),
    }


def send_notification(user_id, message, extra_data=None):
    """
    Smart notification delivery:
    - If user is ONLINE: Send WebSocket notification only
    - If user is OFFLINE: Send FCM push notification only

    Args:
        user_id: Target user ID
        message: Notification message
        title: Notification title (default: "New Notification")
        extra_data: Additional data to send (optional)

    Returns:
        dict: Delivery status and results
    """
    try:
        # Get user
        user = CustomUser.objects.get(id=user_id)

        # Create notification in database
        notification = Notification.objects.create(
            user=user,
            message=message,
        )

        # Prepare notification payload
        notification_payload = {
            "notification_id": str(notification.id),
            "message": message,
        }
        if extra_data:
            notification_payload.update(extra_data)

        # Check if user is online
        if is_user_online(user_id):
            # User is ONLINE - Send via WebSocket
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user_{user_id}",
                    {"type": "send_notification", **notification_payload},
                )
                logger.info(f"✓ WebSocket notification sent to ONLINE user {user_id}")

                return {
                    "success": True,
                    "method": "websocket",
                    "user_status": "online",
                    "notification_id": notification.id,
                }

            except Exception as ws_error:
                logger.error(f"✗ WebSocket failed for user {user_id}: {ws_error}")
                # Don't fallback to FCM if WebSocket fails, just return error
                return {"success": False, "method": "websocket", "error": str(ws_error)}

        else:
            # User is OFFLINE - Send via FCM push notification
            logger.info(f"📱 User {user_id} is OFFLINE - sending FCM push notification")

            # Get user's active devices
            devices = UserDevice.objects.filter(user=user)
            device_tokens = [d.device_token for d in devices if d.device_token]

            if not device_tokens:
                logger.warning(f"⚠️  No device tokens found for OFFLINE user {user_id}")
                return {
                    "success": False,
                    "method": "fcm",
                    "user_status": "offline",
                    "error": "No device tokens registered",
                    "notification_id": notification.id,
                }

            logger.info(
                f"📤 Sending FCM to {len(device_tokens)} device(s) for user {user_id}"
            )

            # Send FCM notification
            fcm_result = send_fcm_notification(
                device_tokens=device_tokens,
                title="New Notification",
                message=message,
                data=extra_data,
            )

            logger.info(
                f"📊 FCM Result for user {user_id}: "
                f"{fcm_result['success']} sent, "
                f"{fcm_result['failure']} failed, "
                f"{fcm_result['invalid_tokens_removed']} invalid tokens removed"
            )

            return {
                "success": fcm_result["success"] > 0,
                "method": "fcm",
                "user_status": "offline",
                "notification_id": notification.id,
                **fcm_result,
            }

    except CustomUser.DoesNotExist:
        logger.error(f"✗ User with id {user_id} does not exist")
        return {"success": False, "error": "User not found"}
    except Exception as e:
        logger.error(f"✗ Notification failed for user {user_id}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def send_bulk_notification(user_ids, message, extra_data=None):
    """
    Send notifications to multiple users

    Args:
        user_ids: List of user IDs
        message: Notification message
        extra_data: Additional data

    Returns:
        dict: Summary of results
    """
    results = {
        "total_users": len(user_ids),
        "websocket_sent": 0,
        "fcm_sent": 0,
        "failed": 0,
        "details": [],
    }

    logger.info(f"📢 Sending bulk notification to {len(user_ids)} users")

    for user_id in user_ids:
        result = send_notification(
            user_id=user_id, message=message, extra_data=extra_data
        )

        if result.get("success"):
            if result.get("method") == "websocket":
                results["websocket_sent"] += 1
            elif result.get("method") == "fcm":
                results["fcm_sent"] += result.get("success", 0)
        else:
            results["failed"] += 1

        results["details"].append(
            {
                "user_id": user_id,
                "success": result.get("success"),
                "method": result.get("method"),
                "status": result.get("user_status"),
            }
        )

    logger.info(
        f"📊 Bulk notification complete: "
        f"{results['websocket_sent']} websocket, "
        f"{results['fcm_sent']} FCM, "
        f"{results['failed']} failed"
    )

    return results
