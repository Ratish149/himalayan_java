from rest_framework import serializers
from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    product = serializers.ReadOnlyField(source='product.id')

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product']
