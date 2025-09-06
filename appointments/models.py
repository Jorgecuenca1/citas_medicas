from django.db import models
from django.conf import settings
from core.models import Room


class AppointmentType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    duration_min = models.PositiveIntegerField(default=30, verbose_name='Duración (minutos)')
    requires_room = models.BooleanField(default=True, verbose_name='Requiere sala')
    requires_resource = models.JSONField(default=list, blank=True, verbose_name='Recursos requeridos')
    buffer_before_min = models.PositiveIntegerField(default=0, verbose_name='Buffer antes (minutos)')
    buffer_after_min = models.PositiveIntegerField(default=0, verbose_name='Buffer después (minutos)')
    
    class Meta:
        db_table = 'appointments_appointmenttype'
        verbose_name = 'Tipo de cita'
        verbose_name_plural = 'Tipos de cita'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.duration_min} min)"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('RESERVADO', 'Reservado'),
        ('CONFIRMADO', 'Confirmado'),
        ('REPROGRAMADO', 'Reprogramado'),
        ('CANCELADO_PAC', 'Cancelado por paciente'),
        ('CANCELADO_CLIN', 'Cancelado por clínica'),
        ('NO_SHOW', 'No asistió'),
        ('ATENDIDO', 'Atendido'),
    ]
    
    slot = models.OneToOneField('availability.Slot', on_delete=models.PROTECT, related_name='appointment')
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='appointments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RESERVADO')
    
    booked_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de reserva')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de confirmación')
    rescheduled_from = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='rescheduled_to')
    
    canceled_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de cancelación')
    canceled_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='canceled_appointments')
    cancel_reason = models.TextField(blank=True, verbose_name='Motivo de cancelación')
    
    checked_in_at = models.DateTimeField(null=True, blank=True, verbose_name='Hora de check-in')
    attended_at = models.DateTimeField(null=True, blank=True, verbose_name='Hora de atención')
    no_show_marked_at = models.DateTimeField(null=True, blank=True, verbose_name='Marcado como no-show')
    
    notes = models.TextField(blank=True, verbose_name='Notas')
    
    class Meta:
        db_table = 'appointments_appointment'
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['-booked_at']
    
    def __str__(self):
        return f"Cita {self.id} - {self.patient} - {self.slot.start_dt}"