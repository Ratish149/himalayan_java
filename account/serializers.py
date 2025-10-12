from rest_framework import serializers

from branch.models import Branch

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
            "id",
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
            "id",
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


class AdminRegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    role = serializers.CharField(max_length=15, required=False)


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()
