from django.db import models
from django.conf import settings


class AuditEvent(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Actor')
    object_type = models.CharField(max_length=50, verbose_name='Tipo de objeto')
    object_id = models.CharField(max_length=50, verbose_name='ID del objeto')
    action = models.CharField(max_length=50, verbose_name='Acción')
    at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha/hora')
    meta = models.JSONField(default=dict, blank=True, verbose_name='Metadatos')
    
    class Meta:
        db_table = 'audit_auditevent'
        verbose_name = 'Evento de auditoría'
        verbose_name_plural = 'Eventos de auditoría'
        ordering = ['-at']
        indexes = [
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['actor', 'at']),
        ]
    
    def __str__(self):
        return f"{self.actor} - {self.action} - {self.object_type}:{self.object_id} - {self.at}"