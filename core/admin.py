from django.contrib import admin
from .models import Specialty, Location, Room


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'timezone', 'active']
    list_filter = ['active']
    search_fields = ['name', 'address']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['location', 'name', 'resource_tags']
    list_filter = ['location']
    search_fields = ['name', 'location__name']