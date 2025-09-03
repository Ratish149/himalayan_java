from django.contrib import admin
from .models import Branch
from unfold.admin import ModelAdmin
# Register your models here.

admin.site.register(Branch,ModelAdmin)
