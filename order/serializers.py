from rest_framework import serializers
from django.db import transaction
from account.serializers import CustomUserSerializer, CustomUserSerializer2
from .models import Order, OrderItem
from branch.serializers import BranchSerializer
from product.serializers import ProductSmallSerializer
from product.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    # Add product details for read operations
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'price']
        
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Auto-set user
    order_number = serializers.CharField(read_only=True)  # Let model generate this
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # Calculated field

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_status', 'order_type',
            'total_price', 'discount', 'user', 'items',
            'branch', 'created_at', 'updated_at', 'special_requests'
        ]
        read_only_fields = ['id', 'order_number', 'total_price', 'created_at', 'updated_at']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required")
        return value

    def validate(self, attrs):
        # Validate that all products exist
        items_data = attrs.get('items', [])
        for item_data in items_data:
            product = item_data.get('product')
            if not isinstance(product, Product):
                raise serializers.ValidationError("Invalid product provided for an order item")
            if not Product.objects.filter(id=product.id).exists():
                raise serializers.ValidationError(
                    f"Product with id {product.id} does not exist."
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        print("Creating order with validated_data:", validated_data)
        
        items_data = validated_data.pop('items')
        
        # Create order first (without items)
        order = Order.objects.create(**validated_data)
        
        if not order:
            raise serializers.ValidationError("Failed to create order")
            
        print(f"Order created: ID={order.id}, Number={order.order_number}")

        total_price = 0
        total_redeem_points = 0

        # Create order items
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            # Calculate price (use provided price or product price * quantity)
            price = item_data.get('price')
            if price is None:
                price = product.price * quantity

            # Validate price
            if price < 0:
                raise serializers.ValidationError("Item price cannot be negative")

            # Accumulate totals
            total_price += price

            # Calculate redeem points
            if product.is_featured:
                points = product.featured_points * quantity
            else:
                points = product.redeem_points * quantity
            total_redeem_points += points

            # Create order item
            OrderItem.objects.create(
                order=order, 
                product=product, 
                quantity=quantity, 
                price=price
            )

        # Update order total price
        order.total_price = total_price
        order.save()

        # Award redeem points to user (but don't deduct here - that's done in view)
        user = self.context['request'].user
        if user and user.is_authenticated:
            user.redeem_points += total_redeem_points
            user.save()

        print(f"Order finalized: Total=${total_price}, Points awarded={total_redeem_points}")
        return order

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if items_data is not None:
            # Clear existing items
            instance.items.all().delete()

            total_price = 0
            total_redeem_points = 0

            # Recreate items
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']

                price = item_data.get('price')
                if price is None:
                    price = product.price * quantity

                total_price += price

                # Calculate points correctly
                if product.is_featured:
                    points = product.featured_points * quantity
                else:
                    points = product.redeem_points * quantity
                total_redeem_points += points

                OrderItem.objects.create(
                    order=instance, 
                    product=product, 
                    quantity=quantity, 
                    price=price
                )

            # Update totals
            instance.total_price = total_price
            
            # Award points to user
            if instance.user:
                instance.user.redeem_points += total_redeem_points
                instance.user.save()

        instance.save()
        return instance


class OrderItemReadSerializer(serializers.ModelSerializer):
    """Read-only representation with robust fallbacks for product details."""
    product = ProductSmallSerializer(read_only=True)
    product_name = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'price']

    def get_product_name(self, obj):
        if obj.product and getattr(obj.product, 'name', None):
            return obj.product.name
        return ''

    def get_product_price(self, obj):
        # Prefer current product price if product exists, otherwise fall back to stored item price
        if obj.product and getattr(obj.product, 'price', None) is not None:
            return obj.product.price
        return obj.price


class OrderSerializer2(serializers.ModelSerializer):
    """Read-only serializer with nested relationships and non-null fallbacks."""
    items = OrderItemReadSerializer(many=True, read_only=True)
    user = CustomUserSerializer2(read_only=True)
    branch = BranchSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_status', 'order_type',
            'total_price', 'discount', 'user', 'branch',
            'created_at', 'updated_at', 'items', 'special_requests'
        ]