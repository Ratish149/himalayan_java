from rest_framework import serializers
from django.db import transaction
from .models import UserRedeem, Redeem
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

class RedeemSerializer(serializers.ModelSerializer):
    sub_category_name = serializers.CharField(source='sub_category.name', read_only=True)
    
    class Meta:
        model = Redeem
        fields = ['id', 'redeem_points', 'sub_category', 'sub_category_name', 'created_at', 'updated_at']


class UserRedeemSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRedeem
        fields = ['id', 'user', 'redeem', 'points_used', 'created_at', 'updated_at']

    def create(self, validated_data):
        redeem = validated_data['redeem']
        redeem_offer = Redeem.objects.get(id=redeem.id)

        if self.context['request'].user.redeem_points < redeem_offer.redeem_points:
            raise ValidationError("Not enough redeem points")

        with transaction.atomic():
            user_redeem = UserRedeem.objects.create(**validated_data)
            self.context['request'].user.redeem_points -= redeem_offer.redeem_points
            self.context['request'].user.save()

        return user_redeem