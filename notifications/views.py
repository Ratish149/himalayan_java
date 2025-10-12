# notifications/views.py

from django.shortcuts import render
from pyfcm import FCMNotification
from rest_framework import generics, permissions, status

# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification, UserDevice
from .serializers import NotificationSerializer
from .utils import send_notification


def test_notifications(request):
    return render(request, "test.html")


# notifications/api_views.py


class SendNotificationAPIView(APIView):
    serializer_class = NotificationSerializer

    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user_id"]
            message = serializer.validated_data["message"]

            notification = Notification.objects.create(user=user, message=message)
            notification.save()

            # Send the real-time notification
            send_notification(user.id, message)

            return Response({"detail": "Notification sent!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationListAPIView(APIView):
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(user=user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class NotificationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class RegisterDeviceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get("device_token")
        platform = request.data.get("platform", "android")
        if not token:
            return Response(
                {"error": "device_token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device, created = UserDevice.objects.update_or_create(
            user=request.user, device_token=token, defaults={"platform": platform}
        )
        return Response({"success": True, "created": created})


key = "BDjOwAcvQKgX3s6GmNw_QCnblT9wvzQQhPz-PxUb-LkgAMTl0HQjqjZzsyn2gY5-MtwD-YHnaCiuS8vaEBHB03A"
push_service = FCMNotification(
    service_account_file=None, credentials=key, project_id="hjava-81254"
)


@api_view(["POST"])
def test_push_notification(request):
    """
    Test FCM push notification
    """
    try:
        user_id = request.data.get("user_id")
        message = request.data.get("message", "Test notification")

        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        from .models import CustomUser, UserDevice

        user = CustomUser.objects.get(id=user_id)
        devices = UserDevice.objects.filter(user=user)
        registration_ids = [d.device_token for d in devices if d.device_token]

        if not registration_ids:
            return Response({"error": "No device tokens found"}, status=400)

        import asyncio

        loop = asyncio.get_event_loop()
        if loop.is_running():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            result = new_loop.run_until_complete(
                push_service.notify_multiple_devices(
                    registration_ids=registration_ids,
                    message_title="Test Notification",
                    message_body=message,
                    sound="Default",
                )
            )
            new_loop.close()
        else:
            result = loop.run_until_complete(
                push_service.notify_multiple_devices(
                    registration_ids=registration_ids,
                    message_title="Test Notification",
                    message_body=message,
                    sound="Default",
                )
            )

        return Response(
            {
                "success": True,
                "message": "Push notification sent",
                "fcm_result": result,
                "devices_count": len(registration_ids),
            }
        )

    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except Exception as e:
        import traceback

        traceback.print_exc()
        return Response({"error": str(e)}, status=500)
