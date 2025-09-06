from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('RECEP', 'Recepción'),
        ('MEDICO', 'Médico'),
        ('PACIENTE', 'Paciente'),
        ('SOPORTE', 'Soporte/BI'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PACIENTE')
    phone = models.CharField(max_length=20, blank=True)
    document_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"