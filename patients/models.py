from django.db import models
from django.conf import settings


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    birthdate = models.DateField(verbose_name='Fecha de nacimiento')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    insurance = models.CharField(max_length=100, blank=True, verbose_name='Aseguradora')
    consent_given_at = models.DateTimeField(null=True, blank=True, verbose_name='Consentimiento otorgado')
    
    class Meta:
        db_table = 'patients_patient'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"