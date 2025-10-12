import json

from channels.generic.websocket import AsyncWebsocketConsumer

from notifications.tracking import user_connected, user_disconnected


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = int(self.scope["url_route"]["kwargs"]["user_id"])
        self.group_name = f"user_{self.user_id}"

        # Mark user online
        user_connected(self.user_id)  # ✅ add this

        # Join group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Mark user offline
        user_disconnected(self.user_id)  # ✅ add this

        # Leave group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        message = event.get("message", "")
        await self.send(text_data=json.dumps({"message": message}))
