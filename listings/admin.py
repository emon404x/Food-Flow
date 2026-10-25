from django.contrib import admin
from .models import FoodListing, FoodPhoto


@admin.action(description="Mark selected Food Listings as Available")
def make_available_listings(modeladmin, request, queryset):
    queryset.update(status=FoodListing.STATUS_AVAILABLE)


@admin.action(description="Mark selected Food Listings as Expired")
def make_expired_listings(modeladmin, request, queryset):
    queryset.update(status=FoodListing.STATUS_EXPIRED)


@admin.register(FoodListing)
class FoodListingAdmin(admin.ModelAdmin):
    list_display = ('food_name', 'donor', 'quantity', 'unit', 'status', 'expires_at', 'created_at')
    list_filter = ('status', 'location__city', 'created_at')
    search_fields = ('food_name', 'description', 'donor__organization_name', 'donor__user__username', 'location__area')
    actions = [make_available_listings, make_expired_listings]
    ordering = ('expires_at',)

@admin.register(FoodPhoto)
class FoodPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'caption', 'created_at')
    search_fields = ('listing__food_name', 'caption')
    readonly_fields = ('created_at',)