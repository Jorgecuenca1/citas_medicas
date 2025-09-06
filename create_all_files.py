import os
import pathlib

# Crear estructura completa del proyecto

# URLs de cada app
urls_content = {
    'accounts/urls.py': '''from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
]
''',
    
    'appointments/urls.py': '''from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('search/', views.appointment_search, name='appointment_search'),
    path('book/<int:slot_id>/', views.appointment_book, name='appointment_book'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/confirm/', views.appointment_confirm, name='appointment_confirm'),
    path('<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('<int:pk>/checkin/', views.appointment_checkin, name='appointment_checkin'),
    path('<int:pk>/attend/', views.appointment_attend, name='appointment_attend'),
    path('<int:pk>/reschedule/', views.appointment_reschedule, name='appointment_reschedule'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/doctors-by-specialty/', views.get_doctors_by_specialty, name='doctors_by_specialty'),
]
''',
    
    'patients/urls.py': '''from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('create/', views.patient_create, name='patient_create'),
    path('profile/create/', views.patient_profile_create, name='patient_profile_create'),
    path('<int:pk>/', views.patient_detail, name='patient_detail'),
    path('<int:pk>/update/', views.patient_update, name='patient_update'),
]
''',
    
    'doctors/urls.py': '''from django.urls import path
from . import views

urlpatterns = [
    path('', views.doctor_list, name='doctor_list'),
    path('<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('schedule/', views.doctor_schedule, name='doctor_schedule'),
    path('patients/', views.doctor_patients, name='doctor_patients'),
]
''',
    
    'reports/urls.py': '''from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('appointments/', views.appointments_report, name='appointments_report'),
    path('occupancy/', views.occupancy_report, name='occupancy_report'),
    path('cancellations/', views.cancellations_report, name='cancellations_report'),
]
''',
}

# Crear archivos de URLs
for filepath, content in urls_content.items():
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filepath}")

# Views faltantes
views_content = {
    'doctors/views.py': '''from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Doctor
from appointments.models import Appointment
from patients.models import Patient


@login_required
def doctor_list(request):
    """Lista de médicos"""
    doctors = Doctor.objects.select_related('user', 'specialty').prefetch_related('locations')
    
    # Filtros
    specialty_id = request.GET.get('specialty')
    location_id = request.GET.get('location')
    
    if specialty_id:
        doctors = doctors.filter(specialty_id=specialty_id)
    if location_id:
        doctors = doctors.filter(locations__id=location_id)
    
    context = {
        'doctors': doctors.filter(active=True),
    }
    return render(request, 'doctors/doctor_list.html', context)


@login_required
def doctor_detail(request, pk):
    """Detalle del médico"""
    doctor = get_object_or_404(Doctor.objects.select_related('user', 'specialty'), pk=pk)
    
    # Próximas citas
    upcoming_appointments = Appointment.objects.filter(
        slot__doctor=doctor,
        slot__start_dt__gte=timezone.now(),
        status__in=['RESERVADO', 'CONFIRMADO']
    ).select_related('patient__user').order_by('slot__start_dt')[:10]
    
    context = {
        'doctor': doctor,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'doctors/doctor_detail.html', context)


@login_required
def doctor_schedule(request):
    """Horario del médico"""
    if request.user.role != 'MEDICO':
        return redirect('dashboard')
    
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return redirect('dashboard')
    
    # Obtener citas de la semana
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    appointments = Appointment.objects.filter(
        slot__doctor=doctor,
        slot__start_dt__date__gte=week_start,
        slot__start_dt__date__lte=week_end
    ).select_related('patient__user', 'slot').order_by('slot__start_dt')
    
    context = {
        'doctor': doctor,
        'appointments': appointments,
        'week_start': week_start,
        'week_end': week_end,
    }
    return render(request, 'doctors/doctor_schedule.html', context)


@login_required
def doctor_patients(request):
    """Pacientes del médico"""
    if request.user.role != 'MEDICO':
        return redirect('dashboard')
    
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return redirect('dashboard')
    
    # Obtener pacientes únicos
    patient_ids = Appointment.objects.filter(
        slot__doctor=doctor
    ).values_list('patient_id', flat=True).distinct()
    
    patients = Patient.objects.filter(
        id__in=patient_ids
    ).select_related('user').order_by('user__last_name', 'user__first_name')
    
    context = {
        'doctor': doctor,
        'patients': patients,
    }
    return render(request, 'doctors/doctor_patients.html', context)
''',
    
    'reports/views.py': '''from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta, date
from appointments.models import Appointment
from doctors.models import Doctor
from patients.models import Patient
from core.models import Location


@login_required
def reports_dashboard(request):
    """Dashboard de reportes"""
    if request.user.role not in ['ADMIN', 'SOPORTE']:
        return redirect('dashboard')
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    context = {
        'total_appointments_month': Appointment.objects.filter(
            slot__start_dt__date__gte=month_start
        ).count(),
        'total_patients': Patient.objects.count(),
        'total_doctors': Doctor.objects.filter(active=True).count(),
        'cancellation_rate': calculate_cancellation_rate(month_start, today),
        'no_show_rate': calculate_no_show_rate(month_start, today),
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
def appointments_report(request):
    """Reporte de citas"""
    if request.user.role not in ['ADMIN', 'SOPORTE']:
        return redirect('dashboard')
    
    # Filtros
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    appointments = Appointment.objects.all()
    
    if date_from:
        appointments = appointments.filter(slot__start_dt__date__gte=date_from)
    if date_to:
        appointments = appointments.filter(slot__start_dt__date__lte=date_to)
    
    # Estadísticas por estado
    stats = appointments.values('status').annotate(count=Count('id'))
    
    context = {
        'appointments': appointments.select_related('patient__user', 'slot__doctor__user')[:100],
        'stats': stats,
        'total': appointments.count(),
    }
    return render(request, 'reports/appointments.html', context)


@login_required
def occupancy_report(request):
    """Reporte de ocupación"""
    if request.user.role not in ['ADMIN', 'SOPORTE']:
        return redirect('dashboard')
    
    # Ocupación por médico
    doctors_stats = []
    for doctor in Doctor.objects.filter(active=True):
        total_slots = doctor.slots.filter(
            start_dt__date__gte=timezone.now().date() - timedelta(days=30)
        ).count()
        occupied_slots = doctor.slots.filter(
            start_dt__date__gte=timezone.now().date() - timedelta(days=30),
            status='OCUPADO'
        ).count()
        
        occupancy_rate = (occupied_slots / total_slots * 100) if total_slots > 0 else 0
        
        doctors_stats.append({
            'doctor': doctor,
            'total_slots': total_slots,
            'occupied_slots': occupied_slots,
            'occupancy_rate': round(occupancy_rate, 2),
        })
    
    context = {
        'doctors_stats': doctors_stats,
    }
    return render(request, 'reports/occupancy.html', context)


@login_required
def cancellations_report(request):
    """Reporte de cancelaciones"""
    if request.user.role not in ['ADMIN', 'SOPORTE']:
        return redirect('dashboard')
    
    # Cancelaciones del último mes
    month_ago = timezone.now().date() - timedelta(days=30)
    
    cancellations = Appointment.objects.filter(
        status__in=['CANCELADO_PAC', 'CANCELADO_CLIN'],
        canceled_at__date__gte=month_ago
    ).select_related('patient__user', 'slot__doctor__user', 'canceled_by')
    
    # Estadísticas
    by_patient = cancellations.filter(status='CANCELADO_PAC').count()
    by_clinic = cancellations.filter(status='CANCELADO_CLIN').count()
    
    context = {
        'cancellations': cancellations.order_by('-canceled_at')[:100],
        'by_patient': by_patient,
        'by_clinic': by_clinic,
        'total': cancellations.count(),
    }
    return render(request, 'reports/cancellations.html', context)


def calculate_cancellation_rate(date_from, date_to):
    """Calcular tasa de cancelación"""
    total = Appointment.objects.filter(
        slot__start_dt__date__gte=date_from,
        slot__start_dt__date__lte=date_to
    ).count()
    
    canceled = Appointment.objects.filter(
        slot__start_dt__date__gte=date_from,
        slot__start_dt__date__lte=date_to,
        status__in=['CANCELADO_PAC', 'CANCELADO_CLIN']
    ).count()
    
    return round((canceled / total * 100), 2) if total > 0 else 0


def calculate_no_show_rate(date_from, date_to):
    """Calcular tasa de no-show"""
    total = Appointment.objects.filter(
        slot__start_dt__date__gte=date_from,
        slot__start_dt__date__lte=date_to
    ).count()
    
    no_shows = Appointment.objects.filter(
        slot__start_dt__date__gte=date_from,
        slot__start_dt__date__lte=date_to,
        status='NO_SHOW'
    ).count()
    
    return round((no_shows / total * 100), 2) if total > 0 else 0
''',
}

# Crear archivos de views
for filepath, content in views_content.items():
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filepath}")

print("\nAll files created successfully!")