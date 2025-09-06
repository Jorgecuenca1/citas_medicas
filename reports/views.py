from django.shortcuts import render, redirect
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
