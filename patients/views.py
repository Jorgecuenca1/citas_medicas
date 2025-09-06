from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.db.models import Q
from .models import Patient
from accounts.models import User
from appointments.models import Appointment
from django.utils import timezone


@login_required
def patient_list(request):
    """Lista de pacientes con búsqueda"""
    patients = Patient.objects.select_related('user')
    
    # Búsqueda
    search = request.GET.get('search')
    if search:
        patients = patients.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__document_id__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    context = {
        'patients': patients.order_by('user__last_name', 'user__first_name'),
        'search': search,
    }
    
    return render(request, 'patients/patient_list.html', context)


@login_required
def patient_detail(request, pk):
    """Detalle de paciente con historial"""
    patient = get_object_or_404(Patient.objects.select_related('user'), pk=pk)
    
    # Obtener todas las citas para los conteos
    all_appointments = Appointment.objects.filter(patient=patient)
    
    # Calcular conteos antes del slice
    upcoming_count = all_appointments.filter(
        slot__start_dt__gte=timezone.now(),
        status__in=['RESERVADO', 'CONFIRMADO']
    ).count()
    
    past_count = all_appointments.filter(
        slot__start_dt__lt=timezone.now()
    ).count()
    
    # Obtener las últimas 20 citas para mostrar
    appointments = all_appointments.select_related(
        'slot__doctor__user', 
        'slot__doctor__specialty',
        'slot__location'
    ).order_by('-slot__start_dt')[:20]
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'upcoming_count': upcoming_count,
        'past_count': past_count,
    }
    
    return render(request, 'patients/patient_detail.html', context)


@login_required
def patient_create(request):
    """Crear nuevo paciente"""
    if request.method == 'POST':
        # Crear usuario
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        document_id = request.POST.get('document_id')
        phone = request.POST.get('phone')
        
        # Verificar que el username no existe
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return render(request, 'patients/patient_form.html', request.POST)
        
        # Verificar que el documento no existe
        if User.objects.filter(document_id=document_id).exists():
            messages.error(request, 'El documento ya está registrado')
            return render(request, 'patients/patient_form.html', request.POST)
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='PACIENTE'
        )
        user.document_id = document_id
        user.phone = phone
        user.set_password('temp123456')  # Contraseña temporal
        user.save()
        
        # Crear perfil de paciente
        patient = Patient.objects.create(
            user=user,
            birthdate=request.POST.get('birthdate'),
            gender=request.POST.get('gender'),
            insurance=request.POST.get('insurance', ''),
            consent_given_at=timezone.now() if request.POST.get('consent') else None
        )
        
        messages.success(request, f'Paciente {user.get_full_name()} creado exitosamente')
        return redirect('patient_detail', pk=patient.pk)
    
    return render(request, 'patients/patient_form.html')


@login_required
def patient_update(request, pk):
    """Actualizar datos del paciente"""
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        # Actualizar usuario
        user = patient.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.document_id = request.POST.get('document_id')
        user.save()
        
        # Actualizar paciente
        patient.birthdate = request.POST.get('birthdate')
        patient.gender = request.POST.get('gender')
        patient.insurance = request.POST.get('insurance', '')
        if request.POST.get('consent') and not patient.consent_given_at:
            patient.consent_given_at = timezone.now()
        patient.save()
        
        messages.success(request, 'Datos del paciente actualizados')
        return redirect('patient_detail', pk=patient.pk)
    
    context = {
        'patient': patient,
        'is_update': True,
    }
    
    return render(request, 'patients/patient_form.html', context)


@login_required
def patient_profile_create(request):
    """Crear perfil de paciente para usuario existente"""
    if hasattr(request.user, 'patient_profile'):
        return redirect('patient_detail', pk=request.user.patient_profile.pk)
    
    if request.method == 'POST':
        patient = Patient.objects.create(
            user=request.user,
            birthdate=request.POST.get('birthdate'),
            gender=request.POST.get('gender'),
            insurance=request.POST.get('insurance', ''),
            consent_given_at=timezone.now() if request.POST.get('consent') else None
        )
        
        messages.success(request, 'Perfil de paciente creado exitosamente')
        return redirect('dashboard')
    
    return render(request, 'patients/patient_profile_form.html')