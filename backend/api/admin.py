# api/admin.py
from django.contrib import admin
from .models import UserProfile, SavedProduct


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SavedProduct)
class SavedProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_title', 'retailer', 'price', 'cultural_match_score', 'saved_at']
    list_filter = ['retailer', 'saved_at']
    search_fields = ['user__username', 'product_title']
    readonly_fields = ['saved_at']