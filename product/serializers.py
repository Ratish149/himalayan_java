from rest_framework import serializers
from .models import Product, ProductAddOns, ProductSize, ProductCategory, SubCategory


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['id','name']


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id','name']


class SubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SubCategory
        fields = ['id','name', 'category']


class ProductAddOnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAddOns
        fields = ['id','name', 'price']


class ProductSerializer(serializers.ModelSerializer):
    size = ProductSizeSerializer(many=True, required=False)
    add_ons = ProductAddOnsSerializer(many=True, required=False)
    sub_category = SubCategorySerializer(read_only=True)  # Add this line
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'description', 'image',
            'image_alt_description', 'size', 'add_ons', 'sub_category'
        ]
    
    def create(self, validated_data):
        size_data = validated_data.pop('size', [])
        add_ons_data = validated_data.pop('add_ons', [])
        sub_category_data = validated_data.pop('sub_category', None)

        # Get the sub_category object
        if sub_category_data is None:
            raise serializers.ValidationError({'sub_category': 'This field is required.'})
        sub_category_obj = SubCategory.objects.get(pk=sub_category_data.id if hasattr(sub_category_data, 'id') else sub_category_data)

        # Create product
        product = Product.objects.create(sub_category=sub_category_obj, **validated_data)

        # Reuse or create size objects
        for size in size_data:
            size_obj, _ = ProductSize.objects.get_or_create(**size)
            product.size.add(size_obj)

        # Always create new add-ons tied to this product
        for add_on in add_ons_data:
            add_on_obj, _ = ProductAddOns.objects.get_or_create(product=product, **add_on)
            product.add_ons.add(add_on_obj)

        return product

class ProductSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image', 'image_alt_description','description','sub_category']


