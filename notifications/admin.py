from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'channel', 'template', 'status', 'sent_at']
    list_filter = ['channel', 'status', 'template']
    search_fields = ['appointment__patient__user__first_name', 'appointment__patient__user__last_name']
    date_hierarchy = 'sent_at'
    raw_id_fields = ['appointment']
    readonly_fields = ['sent_at']