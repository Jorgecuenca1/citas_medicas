from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'birthdate', 'gender', 'insurance', 'consent_given_at']
    list_filter = ['gender', 'insurance']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__document_id']
    date_hierarchy = 'birthdate'
    raw_id_fields = ['user']