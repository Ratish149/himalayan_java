from django.contrib import admin
from unfold.admin import ModelAdmin
# Register your models here.
from .models import Product, ProductAddOns, ProductSize, ProductCategory, SubCategory

admin.site.register(Product,ModelAdmin)
admin.site.register(ProductAddOns,ModelAdmin)
admin.site.register(ProductSize,ModelAdmin)
admin.site.register(ProductCategory,ModelAdmin)
admin.site.register(SubCategory,ModelAdmin)
