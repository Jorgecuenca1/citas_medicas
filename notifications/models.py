from django.db import models
from appointments.models import Appointment


class Notification(models.Model):
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('failed', 'Fallido'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='notifications')
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    template = models.CharField(max_length=50, verbose_name='Plantilla')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de envío')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payload = models.JSONField(default=dict, blank=True, verbose_name='Datos')
    
    class Meta:
        db_table = 'notifications_notification'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.get_channel_display()} - {self.appointment} - {self.get_status_display()}"