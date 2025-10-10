from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as rest_filters
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Product, ProductCategory, SubCategory
from .serializers import (
    ProductCategorySerializer,
    ProductSerializer,
    ProductSmallSerializer,
    SubCategorySerializer,
)


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
    category = filters.NumberFilter(field_name="category__id")

    class Meta:
        model = SubCategory
        fields = ["category"]


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


class SubProductCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


class ProductFilter(filters.FilterSet):
    category = filters.NumberFilter(
        field_name="sub_category__category__id"
    )  # filter products by category id
    sub_category = filters.NumberFilter(
        field_name="sub_category__id"
    )  # filter products by subcategory id

    class Meta:
        model = Product
        fields = ["sub_category"]


class ProductList(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, rest_filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ["name"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProductSmallSerializer
        return ProductSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "role") and hasattr(user, "branch") and user.role == "admin":
            return Product.objects.filter(branch=user.branch)
        return Product.objects.all()

    def create(self, request, *args, **kwargs):
        user = self.request.user
        if hasattr(user, "role") and hasattr(user, "branch") and user.role == "admin":
            request.data["branch"] = user.branch.id
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BranchSpecificProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSmallSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        branch_id = self.request.query_params.get("branch")

        if branch_id:
            # Filter by branch ID from query parameter
            queryset = queryset.filter(branch_id=branch_id)
        elif hasattr(self.request.user, "branch") and self.request.user.branch:
            # Filter by user's branch if no query parameter provided
            queryset = queryset.filter(branch=self.request.user.branch)
        else:
            # No branch specified and user has no branch, return empty queryset
            return Product.objects.none()


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
