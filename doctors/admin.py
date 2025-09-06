from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number', 'specialty', 'active']
    list_filter = ['active', 'specialty', 'locations']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'license_number']
    raw_id_fields = ['user']
    filter_horizontal = ['locations']