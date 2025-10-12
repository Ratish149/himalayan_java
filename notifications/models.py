from django.db import models

from account.models import CustomUser


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message}"


class UserDevice(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="devices"
    )
    device_token = models.CharField(max_length=255, unique=True)  # FCM token
    platform = models.CharField(
        max_length=10, choices=(("android", "Android"), ("ios", "iOS"))
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.device_token}"
