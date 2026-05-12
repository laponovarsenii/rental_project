from django.contrib import admin
from .models import Listing, ViewHistory

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'city', 'price', 'rooms', 'housing_type', 'is_active')
    list_filter = ('housing_type', 'is_active', 'city')
    search_fields = ('title', 'city')

@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ('listing', 'user', 'viewed_at')