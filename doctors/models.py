from django.db import models
from django.conf import settings
from core.models import Specialty, Location


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    license_number = models.CharField(max_length=50, unique=True, verbose_name='Número de licencia')
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, related_name='doctors')
    locations = models.ManyToManyField(Location, related_name='doctors', verbose_name='Sedes')
    bio = models.TextField(blank=True, verbose_name='Biografía')
    active = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        db_table = 'doctors_doctor'
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialty.name}"