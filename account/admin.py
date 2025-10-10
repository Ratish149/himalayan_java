from django.contrib import admin
from unfold.admin import ModelAdmin

# Register your models here.
from .models import CustomUser


class CustomUserAdmin(ModelAdmin):
    list_display = ("full_name", "phone_number", "email", "id")
    list_filter = ("is_active", "is_staff", "role")
    search_fields = ("phone_number", "email")
    ordering = ("-date_joined",)


admin.site.register(CustomUser, CustomUserAdmin)
