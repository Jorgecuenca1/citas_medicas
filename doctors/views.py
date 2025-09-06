from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import timedelta, datetime, date
from .models import Doctor
from appointments.models import Appointment
from availability.models import Slot, TimeOff, ScheduleTemplate
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
    
    # Obtener fecha de referencia (desde parámetro o fecha actual)
    date_str = request.GET.get('date')
    if date_str:
        try:
            reference_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            reference_date = timezone.now().date()
    else:
        reference_date = timezone.now().date()
    
    # Calcular inicio y fin de semana
    week_start = reference_date - timedelta(days=reference_date.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Calcular semanas anterior y siguiente
    prev_week = (week_start - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week = (week_start + timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Obtener citas de la semana
    appointments = Appointment.objects.filter(
        slot__doctor=doctor,
        slot__start_dt__date__gte=week_start,
        slot__start_dt__date__lte=week_end
    ).select_related('patient__user', 'slot').order_by('slot__start_dt')
    
    # Obtener slots disponibles de la semana
    available_slots = Slot.objects.filter(
        doctor=doctor,
        start_dt__date__gte=week_start,
        start_dt__date__lte=week_end,
        status='LIBRE'
    ).order_by('start_dt')
    
    context = {
        'doctor': doctor,
        'appointments': appointments,
        'available_slots': available_slots,
        'week_start': week_start,
        'week_end': week_end,
        'current_date': reference_date,
        'prev_week': prev_week,
        'next_week': next_week,
        'today': timezone.now().date(),
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


@login_required
def doctor_availability(request):
    """Gestión de disponibilidad del médico"""
    if request.user.role != 'MEDICO':
        return redirect('dashboard')
    
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return redirect('dashboard')
    
    # Obtener mes y año desde parámetros o usar el actual
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month and year:
        try:
            current_date = date(int(year), int(month), 1)
        except (ValueError, TypeError):
            current_date = timezone.now().date().replace(day=1)
    else:
        current_date = timezone.now().date().replace(day=1)
    
    # Calcular primer y último día del mes
    if current_date.month == 12:
        next_month = current_date.replace(year=current_date.year + 1, month=1)
    else:
        next_month = current_date.replace(month=current_date.month + 1)
    
    month_start = current_date
    month_end = next_month - timedelta(days=1)
    
    # Navegación de meses
    prev_month = current_date - timedelta(days=1)
    prev_month = prev_month.replace(day=1)
    
    # Obtener slots del mes
    slots = Slot.objects.filter(
        doctor=doctor,
        start_dt__date__gte=month_start,
        start_dt__date__lte=month_end
    ).order_by('start_dt')
    
    # Obtener time-offs del mes
    timeoffs = TimeOff.objects.filter(
        doctor=doctor,
        start_dt__date__gte=month_start,
        start_dt__date__lte=month_end
    ).order_by('start_dt')
    
    # Obtener templates de horario
    templates = ScheduleTemplate.objects.filter(doctor=doctor)
    
    # Agrupar slots por día
    slots_by_day = {}
    for slot in slots:
        day_key = slot.start_dt.date()
        if day_key not in slots_by_day:
            slots_by_day[day_key] = []
        slots_by_day[day_key].append(slot)
    
    # Crear estructura de calendario
    calendar_weeks = []
    current = month_start
    
    # Encontrar el primer lunes
    while current.weekday() != 0:
        current = current - timedelta(days=1)
    
    while current <= month_end:
        week = []
        for i in range(7):
            day_date = current + timedelta(days=i)
            day_slots = slots_by_day.get(day_date, [])
            
            # Verificar si hay time-off
            is_timeoff = timeoffs.filter(
                start_dt__date__lte=day_date,
                end_dt__date__gte=day_date
            ).exists()
            
            # Contar slots disponibles, ocupados y bloqueados
            available = sum(1 for s in day_slots if s.status == 'LIBRE')
            occupied = sum(1 for s in day_slots if s.status == 'OCUPADO')
            blocked = sum(1 for s in day_slots if s.status == 'BLOQUEADO')
            
            week.append({
                'date': day_date,
                'is_current_month': day_date.month == current_date.month,
                'is_today': day_date == timezone.now().date(),
                'is_timeoff': is_timeoff,
                'total_slots': len(day_slots),
                'available': available,
                'occupied': occupied,
                'blocked': blocked,
                'slots': day_slots
            })
        
        calendar_weeks.append(week)
        current = current + timedelta(days=7)
        
        # Si ya pasamos el mes, terminar
        if current.month != month_start.month and current > month_end:
            break
    
    # Calcular estadísticas del mes
    month_stats = {
        'total_slots': 0,
        'available': 0,
        'occupied': 0,
        'blocked': 0
    }
    
    for week in calendar_weeks:
        for day in week:
            if day['is_current_month']:
                month_stats['total_slots'] += day['total_slots']
                month_stats['available'] += day['available']
                month_stats['occupied'] += day['occupied']
                month_stats['blocked'] += day['blocked']
    
    context = {
        'doctor': doctor,
        'current_month': current_date,
        'month_start': month_start,
        'month_end': month_end,
        'prev_month': prev_month,
        'next_month': next_month,
        'calendar_weeks': calendar_weeks,
        'templates': templates,
        'timeoffs': timeoffs,
        'month_stats': month_stats,
        'today': timezone.now().date(),
    }
    
    return render(request, 'doctors/doctor_availability.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_slot_availability(request):
    """Cambiar disponibilidad de un slot específico"""
    if request.user.role != 'MEDICO':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Perfil de médico no encontrado'}, status=404)
    
    slot_id = request.POST.get('slot_id')
    action = request.POST.get('action')  # 'disable' o 'enable'
    
    try:
        slot = Slot.objects.get(id=slot_id, doctor=doctor)
        
        if action == 'disable':
            if slot.status == 'OCUPADO':
                return JsonResponse({'error': 'No se puede deshabilitar un slot con cita'}, status=400)
            slot.status = 'BLOQUEADO'
        elif action == 'enable':
            if slot.status == 'BLOQUEADO':
                slot.status = 'LIBRE'
        else:
            return JsonResponse({'error': 'Acción no válida'}, status=400)
        
        slot.save()
        
        return JsonResponse({
            'success': True,
            'slot_id': slot.id,
            'new_status': slot.status
        })
        
    except Slot.DoesNotExist:
        return JsonResponse({'error': 'Slot no encontrado'}, status=404)


@login_required
@require_http_methods(["POST"])
def add_timeoff(request):
    """Agregar día no disponible"""
    if request.user.role != 'MEDICO':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Perfil de médico no encontrado'}, status=404)
    
    date_str = request.POST.get('date')
    reason = request.POST.get('reason', '')
    
    try:
        timeoff_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Verificar que no haya citas ese día
        existing_appointments = Appointment.objects.filter(
            slot__doctor=doctor,
            slot__start_dt__date=timeoff_date,
            status__in=['RESERVADO', 'CONFIRMADO']
        ).exists()
        
        if existing_appointments:
            return JsonResponse({
                'error': 'No se puede marcar como no disponible, hay citas confirmadas ese día'
            }, status=400)
        
        # Crear TimeOff para todo el día
        start_datetime = timezone.make_aware(datetime.combine(timeoff_date, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(timeoff_date, datetime.max.time()))
        
        # Verificar si ya existe un TimeOff para ese día
        existing_timeoff = TimeOff.objects.filter(
            doctor=doctor,
            start_dt__date=timeoff_date
        ).first()
        
        if existing_timeoff:
            existing_timeoff.reason = reason
            existing_timeoff.save()
            created = False
        else:
            TimeOff.objects.create(
                doctor=doctor,
                start_dt=start_datetime,
                end_dt=end_datetime,
                reason=reason
            )
            created = True
        
        # Marcar todos los slots del día como no disponibles
        Slot.objects.filter(
            doctor=doctor,
            start_dt__date=timeoff_date,
            status='LIBRE'
        ).update(status='BLOQUEADO')
        
        return JsonResponse({
            'success': True,
            'date': timeoff_date.strftime('%Y-%m-%d'),
            'created': created
        })
        
    except ValueError:
        return JsonResponse({'error': 'Fecha inválida'}, status=400)


@login_required
@require_http_methods(["POST"])
def remove_timeoff(request):
    """Quitar día no disponible"""
    if request.user.role != 'MEDICO':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Perfil de médico no encontrado'}, status=404)
    
    date_str = request.POST.get('date')
    
    try:
        timeoff_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Eliminar TimeOff
        TimeOff.objects.filter(
            doctor=doctor,
            start_dt__date=timeoff_date
        ).delete()
        
        # Rehabilitar slots del día
        Slot.objects.filter(
            doctor=doctor,
            start_dt__date=timeoff_date,
            status='BLOQUEADO'
        ).update(status='LIBRE')
        
        return JsonResponse({
            'success': True,
            'date': timeoff_date.strftime('%Y-%m-%d')
        })
        
    except ValueError:
        return JsonResponse({'error': 'Fecha inválida'}, status=400)


@login_required
def get_day_slots(request):
    """Obtener slots de un día específico para el médico"""
    if request.user.role != 'MEDICO':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Perfil de médico no encontrado'}, status=404)
    
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Fecha requerida'}, status=400)
    
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Obtener todos los slots del día
        slots = Slot.objects.filter(
            doctor=doctor,
            start_dt__date=target_date
        ).order_by('start_dt')
        
        # Verificar si hay un TimeOff para ese día
        timeoff = TimeOff.objects.filter(
            doctor=doctor,
            start_dt__date=target_date
        ).first()
        
        slots_data = []
        for slot in slots:
            # Verificar si el slot tiene cita
            appointment = None
            if slot.status == 'OCUPADO':
                try:
                    appointment = Appointment.objects.get(slot=slot)
                    appointment_data = {
                        'id': appointment.id,
                        'patient': appointment.patient.user.get_full_name(),
                        'status': appointment.get_status_display()
                    }
                except Appointment.DoesNotExist:
                    appointment_data = None
            else:
                appointment_data = None
            
            slots_data.append({
                'id': slot.id,
                'start': slot.start_dt.strftime('%H:%M'),
                'end': slot.end_dt.strftime('%H:%M'),
                'status': slot.status,
                'status_display': slot.get_status_display(),
                'appointment': appointment_data
            })
        
        # Calcular conteos correctamente
        available_count = sum(1 for s in slots if s.status == 'LIBRE')
        occupied_count = sum(1 for s in slots if s.status == 'OCUPADO')
        blocked_count = sum(1 for s in slots if s.status == 'BLOQUEADO')
        
        return JsonResponse({
            'success': True,
            'date': target_date.strftime('%Y-%m-%d'),
            'date_formatted': target_date.strftime('%d de %B de %Y'),
            'slots': slots_data,
            'total_slots': len(slots),
            'available': available_count,
            'occupied': occupied_count,
            'blocked': blocked_count,
            'has_timeoff': timeoff is not None,
            'timeoff_reason': timeoff.reason if timeoff else None
        })
        
    except ValueError:
        return JsonResponse({'error': 'Fecha inválida'}, status=400)
