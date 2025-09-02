from django.urls import path
from . import views

urlpatterns = [
    path('category/', views.ProductCategoryList.as_view(), name='category-list'),
    path('subcategory/', views.SubCategoryList.as_view(), name='subcategory-list'),
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('product/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('category/<int:pk>/', views.ProductCategoryDetail.as_view(), name='category-detail'),
    path('subcategory/<int:pk>/', views.SubProductCategoryDetaik.as_view(), name='subcategory-detail'),

]
