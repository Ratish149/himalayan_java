from django.contrib import admin
from .models import Redeem, UserRedeem
from unfold.admin import ModelAdmin

@admin.register(Redeem)
class RedeemAdmin(ModelAdmin):
    list_display = ['sub_category', 'redeem_points', 'created_at']
    list_filter = ['sub_category', 'redeem_points']
    search_fields = ['sub_category__name']

admin.site.register(UserRedeem, ModelAdmin)