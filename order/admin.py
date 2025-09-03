from django.contrib import admin
from unfold.admin import ModelAdmin,TabularInline
from .models import Order,OrderItem


# Register your models here.

class OrderItemInline(TabularInline):
    model = OrderItem
    tab=True


class OrderAdmin(ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['order_number','created_at']

admin.site.register(Order,OrderAdmin)