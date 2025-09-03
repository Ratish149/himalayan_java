from django.contrib import admin
from unfold.admin import ModelAdmin,TabularInline
# Register your models here.
from .models import Product, ProductAddOns, ProductSize, ProductCategory, SubCategory

class ProductAddOnsInline(TabularInline):
    model = ProductAddOns
    tab=True

class ProductAdmin(ModelAdmin):
    inlines = [ProductAddOnsInline]
    list_display = ['name','price','sub_category']

admin.site.register(Product,ProductAdmin)
admin.site.register(ProductAddOns,ModelAdmin)
admin.site.register(ProductSize,ModelAdmin)
admin.site.register(ProductCategory,ModelAdmin)
admin.site.register(SubCategory,ModelAdmin)
