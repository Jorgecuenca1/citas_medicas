from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta, date
import json

from .models import Appointment, AppointmentType
from availability.models import Slot, ScheduleTemplate
from patients.models import Patient
from doctors.models import Doctor
from core.models import Location, Specialty
from audit.models import AuditEvent


@login_required
def appointment_list(request):
    """Lista de citas con filtros"""
    appointments = Appointment.objects.select_related(
        'patient__user', 
        'slot__doctor__user',
        'slot__location'
    )
    
    # Filtros
    status = request.GET.get('status')
    doctor_id = request.GET.get('doctor')
    patient_id = request.GET.get('patient')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if status:
        appointments = appointments.filter(status=status)
    
    if doctor_id:
        appointments = appointments.filter(slot__doctor_id=doctor_id)
    
    if patient_id:
        appointments = appointments.filter(patient_id=patient_id)
    
    if date_from:
        appointments = appointments.filter(slot__start_dt__date__gte=date_from)
    
    if date_to:
        appointments = appointments.filter(slot__start_dt__date__lte=date_to)
    
    # Ordenar por fecha de cita
    appointments = appointments.order_by('-slot__start_dt')
    
    # Paginación
    paginator = Paginator(appointments, 20)
    page = request.GET.get('page')
    appointments = paginator.get_page(page)
    
    context = {
        'appointments': appointments,
        'doctors': Doctor.objects.filter(active=True).select_related('user'),
        'patients': Patient.objects.select_related('user'),
        'statuses': Appointment.STATUS_CHOICES,
    }
    
    return render(request, 'appointments/appointment_list.html', context)


@login_required
def appointment_search(request):
    """Búsqueda de slots disponibles"""
    context = {
        'specialties': Specialty.objects.all(),
        'locations': Location.objects.filter(active=True),
        'appointment_types': AppointmentType.objects.all(),
    }
    
    if request.method == 'POST':
        specialty_id = request.POST.get('specialty')
        location_id = request.POST.get('location')
        doctor_id = request.POST.get('doctor')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        appointment_type_id = request.POST.get('appointment_type')
        
        # Buscar slots disponibles
        slots = Slot.objects.filter(
            status='LIBRE',
            start_dt__gte=timezone.now()
        ).select_related('doctor__user', 'location')
        
        if specialty_id:
            slots = slots.filter(doctor__specialty_id=specialty_id)
        
        if location_id:
            slots = slots.filter(location_id=location_id)
        
        if doctor_id:
            slots = slots.filter(doctor_id=doctor_id)
        
        if date_from:
            slots = slots.filter(start_dt__date__gte=date_from)
        
        if date_to:
            slots = slots.filter(start_dt__date__lte=date_to)
        
        # Agrupar slots por día y limitar a mostrar varios días
        slots = slots.order_by('start_dt')
        
        # Si hay fechas específicas, usar todo el rango
        if date_from and date_to:
            # No limitar cuando hay rango de fechas
            slots = slots[:500]  # Límite más alto para rangos
        else:
            # Para búsquedas sin rango, mostrar hasta 100 slots
            slots = slots[:100]
        
        context['slots'] = slots
        context['search_performed'] = True
    
    return render(request, 'appointments/appointment_search.html', context)


@login_required
def appointment_book(request, slot_id):
    """Reservar una cita"""
    slot = get_object_or_404(Slot, id=slot_id, status='LIBRE')
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        
        # Si el usuario es paciente, usa su propio perfil
        if request.user.role == 'PACIENTE':
            try:
                patient = request.user.patient_profile
            except Patient.DoesNotExist:
                messages.error(request, 'Debe completar su perfil de paciente antes de reservar citas')
                return redirect('patient_profile_create')
        else:
            # Si es recepción o admin, permite seleccionar paciente
            patient_id = request.POST.get('patient_id')
            if not patient_id:
                messages.error(request, 'Debe seleccionar un paciente')
                return redirect('appointment_book', slot_id=slot_id)
            patient = get_object_or_404(Patient, id=patient_id)
        
        # Verificar que no haya conflictos
        existing = Appointment.objects.filter(
            patient=patient,
            slot__start_dt__date=slot.start_dt.date(),
            slot__start_dt__hour=slot.start_dt.hour
        ).exclude(status__in=['CANCELADO_PAC', 'CANCELADO_CLIN']).exists()
        
        if existing:
            messages.error(request, 'El paciente ya tiene una cita en ese horario')
            return redirect('appointment_search')
        
        # Crear la cita
        appointment = Appointment.objects.create(
            slot=slot,
            patient=patient,
            status='RESERVADO',
            notes=notes
        )
        
        # Marcar slot como ocupado
        slot.status = 'OCUPADO'
        slot.save()
        
        # Registrar en auditoría
        AuditEvent.objects.create(
            actor=request.user,
            object_type='Appointment',
            object_id=str(appointment.id),
            action='CREATE',
            meta={'patient': str(patient.id), 'slot': str(slot_id)}
        )
        
        messages.success(request, f'Cita reservada exitosamente para {patient.user.get_full_name()}')
        return redirect('appointment_detail', pk=appointment.id)
    
    # GET request
    context = {
        'slot': slot,
        'is_patient': request.user.role == 'PACIENTE',
    }
    
    # Solo mostrar lista de pacientes si NO es un paciente
    if request.user.role != 'PACIENTE':
        patients = Patient.objects.select_related('user').order_by('user__last_name', 'user__first_name')
        context['patients'] = patients
    else:
        # Verificar que el paciente tenga perfil
        if not hasattr(request.user, 'patient_profile'):
            messages.warning(request, 'Debe completar su perfil antes de reservar citas')
            return redirect('patient_profile_create')
    
    return render(request, 'appointments/appointment_book.html', context)


@login_required
def appointment_detail(request, pk):
    """Detalle de una cita"""
    appointment = get_object_or_404(
        Appointment.objects.select_related(
            'patient__user',
            'slot__doctor__user',
            'slot__location'
        ),
        pk=pk
    )
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
@require_http_methods(["POST"])
def appointment_confirm(request, pk):
    """Confirmar una cita"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if appointment.status != 'RESERVADO':
        messages.error(request, 'Esta cita no puede ser confirmada')
        return redirect('appointment_detail', pk=pk)
    
    appointment.status = 'CONFIRMADO'
    appointment.confirmed_at = timezone.now()
    appointment.save()
    
    # Auditoría
    AuditEvent.objects.create(
        actor=request.user,
        object_type='Appointment',
        object_id=str(appointment.id),
        action='CONFIRM'
    )
    
    messages.success(request, 'Cita confirmada exitosamente')
    return redirect('appointment_detail', pk=pk)


@login_required
@require_http_methods(["POST"])
def appointment_cancel(request, pk):
    """Cancelar una cita"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if appointment.status in ['CANCELADO_PAC', 'CANCELADO_CLIN', 'ATENDIDO']:
        messages.error(request, 'Esta cita no puede ser cancelada')
        return redirect('appointment_detail', pk=pk)
    
    reason = request.POST.get('cancel_reason', '')
    
    # Determinar tipo de cancelación según rol
    if request.user.role == 'PACIENTE':
        appointment.status = 'CANCELADO_PAC'
    else:
        appointment.status = 'CANCELADO_CLIN'
    
    appointment.canceled_at = timezone.now()
    appointment.canceled_by = request.user
    appointment.cancel_reason = reason
    appointment.save()
    
    # Liberar el slot
    slot = appointment.slot
    slot.status = 'LIBRE'
    slot.save()
    
    # Auditoría
    AuditEvent.objects.create(
        actor=request.user,
        object_type='Appointment',
        object_id=str(appointment.id),
        action='CANCEL',
        meta={'reason': reason}
    )
    
    messages.success(request, 'Cita cancelada exitosamente')
    return redirect('appointment_detail', pk=pk)


@login_required
@require_http_methods(["POST"])
def appointment_checkin(request, pk):
    """Registrar llegada del paciente"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if appointment.status != 'CONFIRMADO':
        messages.error(request, 'El paciente debe tener cita confirmada')
        return redirect('appointment_detail', pk=pk)
    
    appointment.checked_in_at = timezone.now()
    appointment.save()
    
    # Auditoría
    AuditEvent.objects.create(
        actor=request.user,
        object_type='Appointment',
        object_id=str(appointment.id),
        action='CHECKIN'
    )
    
    messages.success(request, 'Check-in registrado exitosamente')
    return redirect('appointment_detail', pk=pk)


@login_required
@require_http_methods(["POST"])
def appointment_attend(request, pk):
    """Marcar cita como atendida"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    appointment.status = 'ATENDIDO'
    appointment.attended_at = timezone.now()
    appointment.save()
    
    # Auditoría
    AuditEvent.objects.create(
        actor=request.user,
        object_type='Appointment',
        object_id=str(appointment.id),
        action='ATTEND'
    )
    
    messages.success(request, 'Cita marcada como atendida')
    return redirect('appointment_detail', pk=pk)


@login_required
def appointment_reschedule(request, pk):
    """Reprogramar una cita"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    # Verificar permisos de reprogramación
    can_reschedule = False
    
    if request.user.role == 'ADMIN':
        can_reschedule = True
    elif request.user.role == 'RECEP':
        can_reschedule = True
    elif request.user.role == 'PACIENTE':
        # Paciente solo puede reprogramar sus propias citas
        try:
            if request.user.patient_profile == appointment.patient:
                can_reschedule = True
        except Patient.DoesNotExist:
            pass
    elif request.user.role == 'MEDICO':
        # Médico puede reprogramar sus propias citas
        try:
            if request.user.doctor_profile == appointment.slot.doctor:
                can_reschedule = True
        except Doctor.DoesNotExist:
            pass
    
    if not can_reschedule:
        messages.error(request, 'No tiene permisos para reprogramar esta cita')
        return redirect('appointment_detail', pk=pk)
    
    if appointment.status in ['CANCELADO_PAC', 'CANCELADO_CLIN', 'ATENDIDO']:
        messages.error(request, 'Esta cita no puede ser reprogramada')
        return redirect('appointment_detail', pk=pk)
    
    if request.method == 'POST':
        new_slot_id = request.POST.get('new_slot_id')
        new_slot = get_object_or_404(Slot, id=new_slot_id, status='LIBRE')
        
        # Liberar slot anterior
        old_slot = appointment.slot
        old_slot.status = 'LIBRE'
        old_slot.save()
        
        # Crear nueva cita
        new_appointment = Appointment.objects.create(
            slot=new_slot,
            patient=appointment.patient,
            status='REPROGRAMADO',
            rescheduled_from=appointment,
            notes=appointment.notes
        )
        
        # Marcar nuevo slot como ocupado
        new_slot.status = 'OCUPADO'
        new_slot.save()
        
        # Actualizar cita anterior
        appointment.status = 'REPROGRAMADO'
        appointment.save()
        
        # Auditoría
        AuditEvent.objects.create(
            actor=request.user,
            object_type='Appointment',
            object_id=str(new_appointment.id),
            action='RESCHEDULE',
            meta={'old_appointment': appointment.id}
        )
        
        messages.success(request, 'Cita reprogramada exitosamente')
        return redirect('appointment_detail', pk=new_appointment.id)
    
    # Buscar slots disponibles del mismo doctor
    # Mostrar más opciones para reprogramación (varios días)
    slots = Slot.objects.filter(
        doctor=appointment.slot.doctor,
        status='LIBRE',
        start_dt__gte=timezone.now()
    ).order_by('start_dt')[:100]  # Mostrar más opciones de diferentes días
    
    context = {
        'appointment': appointment,
        'available_slots': slots,
    }
    
    return render(request, 'appointments/appointment_reschedule.html', context)


@login_required
def calendar_view(request):
    """Vista de calendario de citas"""
    # Obtener fecha actual o la especificada
    date_str = request.GET.get('date')
    if date_str:
        current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        current_date = timezone.now().date()
    
    # Obtener citas del día/semana/mes según vista
    view_type = request.GET.get('view', 'week')  # day, week, month
    
    if view_type == 'day':
        start_date = current_date
        end_date = current_date
    elif view_type == 'week':
        start_date = current_date - timedelta(days=current_date.weekday())
        end_date = start_date + timedelta(days=6)
    else:  # month
        start_date = current_date.replace(day=1)
        if current_date.month == 12:
            end_date = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
    
    # Calcular fechas de navegación
    if view_type == 'week':
        prev_date = (start_date - timedelta(days=7)).strftime('%Y-%m-%d')
        next_date = (start_date + timedelta(days=7)).strftime('%Y-%m-%d')
    elif view_type == 'day':
        prev_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
        next_date = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
    else:  # month
        if current_date.month == 1:
            prev_date = current_date.replace(year=current_date.year - 1, month=12, day=1).strftime('%Y-%m-%d')
        else:
            prev_date = current_date.replace(month=current_date.month - 1, day=1).strftime('%Y-%m-%d')
        
        if current_date.month == 12:
            next_date = current_date.replace(year=current_date.year + 1, month=1, day=1).strftime('%Y-%m-%d')
        else:
            next_date = current_date.replace(month=current_date.month + 1, day=1).strftime('%Y-%m-%d')
    
    # Filtrar por doctor si es necesario
    doctor_id = request.GET.get('doctor')
    appointments = Appointment.objects.filter(
        slot__start_dt__date__gte=start_date,
        slot__start_dt__date__lte=end_date
    ).select_related('patient__user', 'slot__doctor__user', 'slot__location')
    
    if doctor_id:
        appointments = appointments.filter(slot__doctor_id=doctor_id)
    
    # Si el usuario es médico, mostrar solo sus citas
    if request.user.role == 'MEDICO':
        try:
            doctor = request.user.doctor_profile
            appointments = appointments.filter(slot__doctor=doctor)
        except Doctor.DoesNotExist:
            appointments = Appointment.objects.none()
    
    # Si el usuario es paciente, mostrar solo sus citas
    if request.user.role == 'PACIENTE':
        try:
            patient = request.user.patient_profile
            appointments = appointments.filter(patient=patient)
        except Patient.DoesNotExist:
            appointments = Appointment.objects.none()
    
    context = {
        'appointments': appointments,
        'current_date': current_date,
        'start_date': start_date,
        'end_date': end_date,
        'view_type': view_type,
        'prev_date': prev_date,
        'next_date': next_date,
        'doctors': Doctor.objects.filter(active=True).select_related('user') if request.user.role != 'PACIENTE' else None,
    }
    
    return render(request, 'appointments/calendar.html', context)


@login_required
def patient_appointments(request):
    """Lista de todas las citas del paciente"""
    if request.user.role != 'PACIENTE':
        messages.error(request, 'Esta vista es solo para pacientes')
        return redirect('dashboard')
    
    try:
        patient = request.user.patient_profile
    except Patient.DoesNotExist:
        messages.warning(request, 'Debe completar su perfil de paciente')
        return redirect('patient_profile_create')
    
    # Filtros
    status = request.GET.get('status', 'upcoming')  # upcoming, past, all
    
    appointments = Appointment.objects.filter(patient=patient).select_related(
        'slot__doctor__user',
        'slot__doctor__specialty',
        'slot__location'
    )
    
    if status == 'upcoming':
        appointments = appointments.filter(
            slot__start_dt__gte=timezone.now()
        ).exclude(status__in=['CANCELADO_PAC', 'CANCELADO_CLIN'])
    elif status == 'past':
        appointments = appointments.filter(
            slot__start_dt__lt=timezone.now()
        )
    # si es 'all', no aplicar filtro adicional
    
    appointments = appointments.order_by('-slot__start_dt' if status == 'past' else 'slot__start_dt')
    
    # Paginación
    paginator = Paginator(appointments, 10)
    page = request.GET.get('page')
    appointments = paginator.get_page(page)
    
    context = {
        'appointments': appointments,
        'status_filter': status,
        'patient': patient,
    }
    
    return render(request, 'appointments/patient_appointments.html', context)


@login_required
def get_doctors_by_specialty(request):
    """API endpoint para obtener médicos por especialidad"""
    specialty_id = request.GET.get('specialty_id')
    doctors = Doctor.objects.filter(
        specialty_id=specialty_id,
        active=True
    ).select_related('user').values('id', 'user__first_name', 'user__last_name')
    
    return JsonResponse(list(doctors), safe=False)