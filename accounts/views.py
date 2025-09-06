from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.utils import timezone
from .models import User
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from availability.models import Slot


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {user.get_full_name() or user.username}')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente')
    return redirect('login')


@login_required
def dashboard_view(request):
    context = {
        'user': request.user,
    }
    
    # Dashboard específico por rol
    if request.user.role == 'ADMIN':
        # Estadísticas para admin
        context.update({
            'total_patients': Patient.objects.count(),
            'total_doctors': Doctor.objects.filter(active=True).count(),
            'total_appointments': Appointment.objects.count(),
            'today_appointments': Appointment.objects.filter(
                slot__start_dt__date=timezone.now().date()
            ).count(),
            'pending_appointments': Appointment.objects.filter(
                status='RESERVADO'
            ).count(),
            'recent_appointments': Appointment.objects.select_related(
                'patient__user', 'slot__doctor__user'
            ).order_by('-booked_at')[:10],
        })
        return render(request, 'accounts/dashboard_admin.html', context)
    
    elif request.user.role == 'RECEP':
        # Dashboard para recepción
        today = timezone.now().date()
        context.update({
            'today_appointments': Appointment.objects.filter(
                slot__start_dt__date=today
            ).select_related('patient__user', 'slot__doctor__user').order_by('slot__start_dt'),
            'pending_confirmations': Appointment.objects.filter(
                status='RESERVADO'
            ).select_related('patient__user', 'slot__doctor__user')[:10],
            'available_slots_today': Slot.objects.filter(
                start_dt__date=today,
                status='LIBRE'
            ).count(),
        })
        return render(request, 'accounts/dashboard_reception.html', context)
    
    elif request.user.role == 'MEDICO':
        # Dashboard para médicos
        try:
            doctor = request.user.doctor_profile
            today = timezone.now().date()
            context.update({
                'doctor': doctor,
                'today_appointments': Appointment.objects.filter(
                    slot__doctor=doctor,
                    slot__start_dt__date=today
                ).select_related('patient__user').order_by('slot__start_dt'),
                'week_appointments': Appointment.objects.filter(
                    slot__doctor=doctor,
                    slot__start_dt__date__gte=today,
                    slot__start_dt__date__lt=today + timedelta(days=7)
                ).count(),
                'pending_patients': Appointment.objects.filter(
                    slot__doctor=doctor,
                    status__in=['RESERVADO', 'CONFIRMADO']
                ).count(),
            })
            return render(request, 'accounts/dashboard_doctor.html', context)
        except Doctor.DoesNotExist:
            messages.error(request, 'No tienes un perfil de médico asociado')
            return redirect('profile')
    
    elif request.user.role == 'PACIENTE':
        # Dashboard para pacientes
        try:
            patient = request.user.patient_profile
            context.update({
                'patient': patient,
                'upcoming_appointments': Appointment.objects.filter(
                    patient=patient,
                    slot__start_dt__gte=timezone.now(),
                    status__in=['RESERVADO', 'CONFIRMADO']
                ).select_related('slot__doctor__user', 'slot__location').order_by('slot__start_dt')[:5],
                'past_appointments': Appointment.objects.filter(
                    patient=patient,
                    slot__start_dt__lt=timezone.now()
                ).select_related('slot__doctor__user').order_by('-slot__start_dt')[:5],
                'total_appointments': Appointment.objects.filter(patient=patient).count(),
            })
            return render(request, 'accounts/dashboard_patient.html', context)
        except Patient.DoesNotExist:
            messages.warning(request, 'Por favor completa tu perfil de paciente')
            return redirect('patient_profile_create')
    
    # Dashboard genérico
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        # Actualizar perfil
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.save()
        messages.success(request, 'Perfil actualizado exitosamente')
        return redirect('profile')
    
    return render(request, 'accounts/profile.html', {'user': request.user})