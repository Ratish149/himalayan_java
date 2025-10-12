from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Notification, UserDevice


# Register your models here.
class NotificationAdmin(ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("user", "is_read")
    search_fields = ("user", "message")
    ordering = ("-created_at",)


class UserDeviceAdmin(ModelAdmin):
    list_display = ("user", "device_token", "platform", "created_at")
    list_filter = ("user", "platform")
    search_fields = ("user", "device_token")
    ordering = ("-created_at",)


admin.site.register(Notification, NotificationAdmin)
admin.site.register(UserDevice, UserDeviceAdmin)
