from .models import CustomUser
from rest_framework import serializers

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('full_name', 'email', 'phone_number', 'profile_picture', 'redeem_points')