from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Notification


# Register your models here.
class NotificationAdmin(ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("user", "is_read")
    search_fields = ("user", "message")
    ordering = ("-created_at",)


admin.site.register(Notification, NotificationAdmin)
