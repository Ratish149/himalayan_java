from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "full_name",
            "email",
            "phone_number",
            "profile_picture",
            "redeem_points",
            "created_at",
            "updated_at",
            "branch",
            "role",
        )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "full_name",
            "email",
            "phone_number",
            "profile_picture",
            "redeem_points",
            "created_at",
            "updated_at",
            "branch",
            "role",
        )


class CustomUserSerializer2(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "full_name",
            "email",
            "phone_number",
            "profile_picture",
            "redeem_points",
            "created_at",
            "updated_at",
            "branch",
            "role",
        )


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()
