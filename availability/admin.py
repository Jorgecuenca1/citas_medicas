from django.contrib import admin
from .models import ScheduleTemplate, TimeOff, Holiday, Slot


@admin.register(ScheduleTemplate)
class ScheduleTemplateAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'location', 'weekday', 'start_time', 'end_time', 'slot_every_min']
    list_filter = ['doctor', 'location', 'weekday']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name']
    ordering = ['doctor', 'weekday', 'start_time']


@admin.register(TimeOff)
class TimeOffAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'start_dt', 'end_dt', 'reason']
    list_filter = ['doctor']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name', 'reason']
    date_hierarchy = 'start_dt'


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location']
    list_filter = ['location']
    search_fields = ['name']
    date_hierarchy = 'date'


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'location', 'start_dt', 'end_dt', 'status', 'room']
    list_filter = ['status', 'doctor', 'location', 'source']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name']
    date_hierarchy = 'start_dt'
    raw_id_fields = ['doctor', 'room', 'appointment_type']