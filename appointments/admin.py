from django.contrib import admin
from .models import AppointmentType, Appointment


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_min', 'requires_room', 'buffer_before_min', 'buffer_after_min']
    list_filter = ['requires_room']
    search_fields = ['name']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'slot', 'status', 'booked_at']
    list_filter = ['status', 'booked_at', 'slot__doctor']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'patient__user__document_id']
    date_hierarchy = 'booked_at'
    raw_id_fields = ['slot', 'patient', 'canceled_by', 'rescheduled_from']
    readonly_fields = ['booked_at']