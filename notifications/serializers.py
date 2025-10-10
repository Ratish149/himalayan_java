# notifications/serializers.py
from rest_framework import serializers

from account.models import CustomUser


class NotificationSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    message = serializers.CharField(max_length=255)
