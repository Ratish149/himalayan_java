from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Order

# Register your models here.
admin.site.register(Order,ModelAdmin)