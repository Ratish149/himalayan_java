from rest_framework import serializers

from account.serializers import CustomUserSerializer, CustomUserSerializer2
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
        fields = [
            'id', 'order_number', 'order_status', 'order_type',
            'total_price', 'discount', 'user', 'items',
            'branch', 'created_at', 'updated_at', 'special_requests'

        ]

    def create(self, validated_data):
        print(validated_data)

        print(validated_data['items'])
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        total_redeem_points = 0
        total_price = 0

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            if not Product.objects.filter(id=product.id).exists():
                raise serializers.ValidationError(f"Product with id {product.id} does not exist.")

            price = item_data.get('price') or (product.price * quantity)

            # accumulate price + points
            total_price += price
            # points = product.redeem_points * quantity

            if product.is_featured:
                points = product.featured_points * quantity
            else:
                points = product.redeem_points * quantity
            total_redeem_points += points
            print(total_redeem_points)

            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)

        # update totals
        order.total_price = total_price
        order.save()
        user=self.context['request'].user

        if user:
            user.redeem_points += total_redeem_points
            user.save()

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        order = super().update(instance, validated_data)

        if items_data is not None:
            order.items.all().delete()

            total_redeem_points = 0
            total_price = 0

            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']

                print(product)
                print(product.redeem_points)

                price = item_data.get('price') or (product.price * quantity)

                total_price += price
                points = product.redeem_points * quantity
                if product.is_featured:
                    points += product.featured_points * quantity
                total_redeem_points += points

                OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)

            order.total_price = total_price
            order.save()

            if order.user:
                order.user.redeem_points += total_redeem_points
                order.user.save()

        return order


class OrderSerializer2(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True)
    user=CustomUserSerializer2()
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_status', 'order_type',
            'total_price', 'discount', 'user', 'branch',
            'created_at', 'updated_at', 'items'
        ]