from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Redeem, UserRedeem
from rest_framework import serializers as drf_serializers


class RedeemSerializer(serializers.ModelSerializer):
    sub_category_name = serializers.CharField(source='sub_category.name', read_only=True)
    category_id = serializers.IntegerField(source='sub_category.category.id', read_only=True)
    category_name = serializers.CharField(source='sub_category.category.name', read_only=True)

    class Meta:
        model = Redeem
        fields = ['id', 'redeem_points', 'sub_category', 'sub_category_name', 'category_id', 'category_name', 'created_at', 'updated_at']


class UserRedeemSerializer(serializers.ModelSerializer):
    redeem_name = serializers.CharField(source='redeem.sub_category.name', read_only=True)

    class Meta:
        model = UserRedeem
        fields = ['id', 'redeem', 'redeem_name', 'points_used', 'created_at', 'updated_at']
        read_only_fields = ['points_used', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        redeem_offer = validated_data['redeem']

        if user.redeem_points < redeem_offer.redeem_points:
            raise ValidationError("Not enough redeem points.")

        with transaction.atomic():
            user_redeem = UserRedeem.objects.create(user=user, **validated_data)
            user.redeem_points -= redeem_offer.redeem_points
            user.save()

        return user_redeem


class UserRedeemReadSerializer(serializers.ModelSerializer):
    """Read-only serializer with nested redeem and category info."""
    redeem = RedeemSerializer(read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserRedeem
        fields = ['id', 'redeem', 'points_used', 'user_full_name', 'user_email', 'created_at', 'updated_at']
