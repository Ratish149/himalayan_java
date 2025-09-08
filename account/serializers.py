from rest_framework import serializers
from .models import CustomUser
from order.models import Order  # ✅ import from order app


class UserOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'order_status', 'order_type', 'total_price', 'discount', 'created_at']


class CustomUserSerializer(serializers.ModelSerializer):
    orders = UserOrderSerializer(many=True, read_only=True, source="order_set")  # ✅ link to related orders

    class Meta:
        model = CustomUser
        fields = (
            'full_name',
            'email',
            'phone_number',
            'profile_picture',
            'redeem_points',
            'created_at',
            'updated_at',
            'orders',   
        )

class CustomUserSerializer2(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'full_name',
            'email',
            'phone_number',
            'profile_picture',
            'redeem_points',
            'created_at',
            'updated_at',
        )

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()
