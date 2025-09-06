from django.db import models
from core.models import Location, Specialty, Room
from doctors.models import Doctor
from appointments.models import AppointmentType


class ScheduleTemplate(models.Model):
    WEEKDAY_CHOICES = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedule_templates')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, null=True, blank=True)
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES, verbose_name='Día de la semana')
    start_time = models.TimeField(verbose_name='Hora inicio')
    end_time = models.TimeField(verbose_name='Hora fin')
    slot_every_min = models.PositiveIntegerField(default=20, verbose_name='Duración de slot (minutos)')
    max_overbooking = models.PositiveIntegerField(default=0, verbose_name='Máximo sobrecupo')
    
    class Meta:
        db_table = 'availability_scheduletpl'
        verbose_name = 'Plantilla de horario'
        verbose_name_plural = 'Plantillas de horario'
        unique_together = ['doctor', 'location', 'weekday', 'start_time', 'end_time']
        ordering = ['doctor', 'weekday', 'start_time']
    
    def __str__(self):
        return f"{self.doctor} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class TimeOff(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='time_offs')
    start_dt = models.DateTimeField(verbose_name='Fecha/hora inicio')
    end_dt = models.DateTimeField(verbose_name='Fecha/hora fin')
    reason = models.CharField(max_length=200, blank=True, verbose_name='Motivo')
    
    class Meta:
        db_table = 'availability_timeoff'
        verbose_name = 'Ausencia'
        verbose_name_plural = 'Ausencias'
        ordering = ['-start_dt']
    
    def __str__(self):
        return f"{self.doctor} - {self.start_dt} a {self.end_dt}"


class Holiday(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, related_name='holidays')
    date = models.DateField(verbose_name='Fecha')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    
    class Meta:
        db_table = 'availability_holiday'
        verbose_name = 'Feriado'
        verbose_name_plural = 'Feriados'
        unique_together = ['location', 'date']
        ordering = ['date']
    
    def __str__(self):
        location_str = f"{self.location.name} - " if self.location else "Global - "
        return f"{location_str}{self.name} ({self.date})"


class Slot(models.Model):
    STATUS_CHOICES = [
        ('LIBRE', 'Libre'),
        ('BLOQUEADO', 'Bloqueado'),
        ('OCUPADO', 'Ocupado'),
    ]
    
    SOURCE_CHOICES = [
        ('TPL', 'Plantilla'),
        ('EXCEPTION', 'Excepción'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='slots')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.SET_NULL, null=True, blank=True)
    
    start_dt = models.DateTimeField(verbose_name='Fecha/hora inicio')
    end_dt = models.DateTimeField(verbose_name='Fecha/hora fin')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='LIBRE')
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='TPL')
    
    class Meta:
        db_table = 'availability_slot'
        verbose_name = 'Franja disponible'
        verbose_name_plural = 'Franjas disponibles'
        indexes = [
            models.Index(fields=['doctor', 'start_dt']),
            models.Index(fields=['location', 'start_dt']),
        ]
        unique_together = ['doctor', 'start_dt', 'room']
        ordering = ['start_dt']
    
    def __str__(self):
        return f"{self.doctor} - {self.start_dt} ({self.status})"