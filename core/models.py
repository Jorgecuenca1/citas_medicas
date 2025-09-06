from django.db import models


class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    code = models.CharField(max_length=10, unique=True, verbose_name='Código')
    
    class Meta:
        db_table = 'core_specialty'
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    address = models.TextField(verbose_name='Dirección')
    timezone = models.CharField(max_length=50, default='America/Bogota', verbose_name='Zona horaria')
    active = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        db_table = 'core_location'
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Room(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=50, verbose_name='Nombre')
    resource_tags = models.JSONField(default=list, blank=True, verbose_name='Recursos disponibles')
    
    class Meta:
        db_table = 'core_room'
        verbose_name = 'Sala/Consultorio'
        verbose_name_plural = 'Salas/Consultorios'
        unique_together = ['location', 'name']
        ordering = ['location', 'name']
    
    def __str__(self):
        return f"{self.location.name} - {self.name}"