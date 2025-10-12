import logging

logger = logging.getLogger("notifications")

# Simple in-memory tracker
online_users = set()


def user_connected(user_id):
    online_users.add(user_id)
    logger.info(f"✓ User {user_id} is now ONLINE")


def user_disconnected(user_id):
    online_users.discard(user_id)
    logger.info(f"✓ User {user_id} is now OFFLINE")


def is_user_online(user_id):
    return user_id in online_users
