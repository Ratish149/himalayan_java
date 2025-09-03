from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as rest_filters
from .models import Product, ProductCategory, SubCategory
from .serializers import ProductSerializer, ProductCategorySerializer, ProductSmallSerializer, SubCategorySerializer



class ProductCategoryList(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = ProductCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class SubCategoryFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name="category__id")  # filter subcategories by category id

    class Meta:
        model = SubCategory
        fields = ['category']

class SubCategoryList(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SubCategoryFilter

    def create(self, request, *args, **kwargs):
        serializer = SubCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SubProductCategoryDetaik(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

class ProductFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name="sub_category__category__id")  # filter products by category id
    sub_category = filters.NumberFilter(field_name="sub_category__id")  # filter products by subcategory id

    class Meta:
        model = Product
        fields = ['sub_category']


class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, rest_filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductSmallSerializer
        return ProductSerializer

    def create(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer




