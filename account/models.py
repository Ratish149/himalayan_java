from django.contrib.auth.models import AbstractUser
from django.db import models

from branch.models import Branch


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("superadmin", "Superadmin"),
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("staff", "Staff"),
    )

    full_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    profile_picture = models.FileField(
        upload_to="profile_pictures", null=True, blank=True
    )
    alt_delivery_address = models.TextField(null=True, blank=True)
    redeem_points = models.PositiveIntegerField(default=0)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="")

    # Link admins (or staff) to branches
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, null=True, blank=True, related_name="users"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.username
