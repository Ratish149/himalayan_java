from django.contrib import admin
from .models import Favorite
from unfold.admin import ModelAdmin

# Register your models here.
admin.site.register(Favorite,ModelAdmin)