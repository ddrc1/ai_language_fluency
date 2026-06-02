"""
Admin configuration for the login module.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('username', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
