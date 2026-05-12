from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)