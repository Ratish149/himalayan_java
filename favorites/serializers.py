from rest_framework import serializers
from .models import Favorite

class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")
    product = serializers.PrimaryKeyRelatedField(
        queryset=Favorite._meta.get_field("product").related_model.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ["id", "user", "product", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        product = attrs.get("product")
        if Favorite.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError({"product": "This product is already in favorites."})
        return attrs
