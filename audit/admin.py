from django.contrib import admin
from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'object_type', 'object_id', 'at']
    list_filter = ['action', 'object_type']
    search_fields = ['actor__username', 'object_type', 'object_id', 'action']
    date_hierarchy = 'at'
    readonly_fields = ['at']
    raw_id_fields = ['actor']