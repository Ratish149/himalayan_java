from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'order_status', 'total_price', 'user', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        total_redeem_points = 0

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            if not Product.objects.filter(id=product.id).exists():
                raise serializers.ValidationError(f"Product with id {product.id} does not exist.")

            # If price is not given, calculate from product.price
            price = item_data.get('price') or (product.price * quantity)

            # Calculate redeem points
            points = product.redeem_points * quantity
            if product.is_featured:
                points += product.featured_points * quantity

            total_redeem_points += points

            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)

        # Update user’s redeem points
        if order.user:
            order.user.redeem_points += total_redeem_points
            order.user.save()

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        order = super().update(instance, validated_data)

        if items_data is not None:
            # Remove old items
            order.items.all().delete()

            total_redeem_points = 0
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']

                price = item_data.get('price') or (product.price * quantity)

                points = product.redeem_points * quantity
                if product.is_featured:
                    points += product.featured_points * quantity

                total_redeem_points += points

                OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)

            # Reset and recalculate user’s redeem points
            if order.user:
                # careful: you might want to subtract old earned points first
                order.user.redeem_points += total_redeem_points
                order.user.save()

        return order
