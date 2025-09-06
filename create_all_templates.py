import os
import pathlib

# Diccionario con todos los templates HTML
templates = {
    # Login
    'templates/accounts/login.html': '''{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar Sesión - Sistema de Citas Médicas</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 40px;
            width: 100%;
            max-width: 400px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-header i {
            font-size: 48px;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <i class="bi bi-hospital"></i>
            <h2 class="mt-3">Sistema de Citas Médicas</h2>
            <p class="text-muted">Ingrese sus credenciales</p>
        </div>
        
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags|default:'info' }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        <form method="post">
            {% csrf_token %}
            <div class="mb-3">
                <label for="username" class="form-label">Usuario</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-person"></i></span>
                    <input type="text" class="form-control" id="username" name="username" required autofocus>
                </div>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Contraseña</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock"></i></span>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
            </div>
            <button type="submit" class="btn btn-primary w-100">
                <i class="bi bi-box-arrow-in-right"></i> Iniciar Sesión
            </button>
        </form>
        
        <div class="text-center mt-3">
            <small class="text-muted">© 2025 Clínica Médica - Todos los derechos reservados</small>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
''',

    # Dashboard Admin
    'templates/accounts/dashboard_admin.html': '''{% extends 'base.html' %}
{% block title %}Dashboard - Administrador{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Dashboard Administrativo</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <button type="button" class="btn btn-sm btn-outline-secondary">
            <i class="bi bi-calendar"></i> {{ today|date:"d/m/Y" }}
        </button>
    </div>
</div>

<div class="row">
    <div class="col-md-3">
        <div class="card stat-card primary">
            <div class="card-body">
                <h5 class="card-title">Pacientes</h5>
                <h2 class="text-primary">{{ total_patients }}</h2>
                <p class="text-muted mb-0">Total registrados</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card success">
            <div class="card-body">
                <h5 class="card-title">Médicos</h5>
                <h2 class="text-success">{{ total_doctors }}</h2>
                <p class="text-muted mb-0">Activos</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card warning">
            <div class="card-body">
                <h5 class="card-title">Citas Hoy</h5>
                <h2 class="text-warning">{{ today_appointments }}</h2>
                <p class="text-muted mb-0">Programadas</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card info">
            <div class="card-body">
                <h5 class="card-title">Pendientes</h5>
                <h2 class="text-info">{{ pending_appointments }}</h2>
                <p class="text-muted mb-0">Por confirmar</p>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Citas Recientes</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Fecha/Hora</th>
                                <th>Paciente</th>
                                <th>Médico</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for appointment in recent_appointments %}
                            <tr>
                                <td>{{ appointment.slot.start_dt|date:"d/m/Y H:i" }}</td>
                                <td>{{ appointment.patient.user.get_full_name }}</td>
                                <td>Dr. {{ appointment.slot.doctor.user.get_full_name }}</td>
                                <td>
                                    {% if appointment.status == 'RESERVADO' %}
                                        <span class="badge bg-warning">Reservado</span>
                                    {% elif appointment.status == 'CONFIRMADO' %}
                                        <span class="badge bg-success">Confirmado</span>
                                    {% elif appointment.status == 'ATENDIDO' %}
                                        <span class="badge bg-primary">Atendido</span>
                                    {% elif appointment.status == 'NO_SHOW' %}
                                        <span class="badge bg-danger">No asistió</span>
                                    {% else %}
                                        <span class="badge bg-secondary">{{ appointment.get_status_display }}</span>
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="{% url 'appointment_detail' appointment.id %}" class="btn btn-sm btn-outline-primary">
                                        <i class="bi bi-eye"></i> Ver
                                    </a>
                                </td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="5" class="text-center">No hay citas recientes</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Accesos Rápidos</h5>
            </div>
            <div class="card-body">
                <div class="list-group">
                    <a href="{% url 'appointment_search' %}" class="list-group-item list-group-item-action">
                        <i class="bi bi-search"></i> Buscar horarios disponibles
                    </a>
                    <a href="{% url 'patient_create' %}" class="list-group-item list-group-item-action">
                        <i class="bi bi-person-plus"></i> Registrar nuevo paciente
                    </a>
                    <a href="{% url 'calendar' %}" class="list-group-item list-group-item-action">
                        <i class="bi bi-calendar-week"></i> Ver calendario de citas
                    </a>
                    <a href="{% url 'reports_dashboard' %}" class="list-group-item list-group-item-action">
                        <i class="bi bi-graph-up"></i> Ver reportes
                    </a>
                    <a href="/admin/" class="list-group-item list-group-item-action">
                        <i class="bi bi-gear"></i> Configuración del sistema
                    </a>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Estadísticas Rápidas</h5>
            </div>
            <div class="card-body">
                <canvas id="statsChart"></canvas>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx = document.getElementById('statsChart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Confirmadas', 'Pendientes', 'Atendidas', 'Canceladas'],
        datasets: [{
            data: [30, 15, 45, 10],
            backgroundColor: [
                'rgba(40, 167, 69, 0.8)',
                'rgba(255, 193, 7, 0.8)',
                'rgba(13, 110, 253, 0.8)',
                'rgba(220, 53, 69, 0.8)'
            ]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});
</script>
{% endblock %}
''',

    # Dashboard Recepción
    'templates/accounts/dashboard_reception.html': '''{% extends 'base.html' %}
{% block title %}Dashboard - Recepción{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Panel de Recepción</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <a href="{% url 'appointment_search' %}" class="btn btn-primary">
            <i class="bi bi-calendar-plus"></i> Nueva Cita
        </a>
    </div>
</div>

<div class="row">
    <div class="col-md-4">
        <div class="card stat-card warning">
            <div class="card-body">
                <h5 class="card-title">Citas de Hoy</h5>
                <h2 class="text-warning">{{ today_appointments.count }}</h2>
                <p class="text-muted mb-0">Programadas para hoy</p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card stat-card info">
            <div class="card-body">
                <h5 class="card-title">Por Confirmar</h5>
                <h2 class="text-info">{{ pending_confirmations.count }}</h2>
                <p class="text-muted mb-0">Requieren confirmación</p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card stat-card success">
            <div class="card-body">
                <h5 class="card-title">Slots Libres Hoy</h5>
                <h2 class="text-success">{{ available_slots_today }}</h2>
                <p class="text-muted mb-0">Disponibles</p>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Citas de Hoy</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Hora</th>
                                <th>Paciente</th>
                                <th>Médico</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for appointment in today_appointments %}
                            <tr>
                                <td>{{ appointment.slot.start_dt|date:"H:i" }}</td>
                                <td>
                                    {{ appointment.patient.user.get_full_name }}<br>
                                    <small class="text-muted">Doc: {{ appointment.patient.user.document_id }}</small>
                                </td>
                                <td>Dr. {{ appointment.slot.doctor.user.get_full_name }}</td>
                                <td>
                                    {% if appointment.status == 'CONFIRMADO' %}
                                        {% if appointment.checked_in_at %}
                                            <span class="badge bg-info">Check-in OK</span>
                                        {% else %}
                                            <span class="badge bg-success">Confirmado</span>
                                        {% endif %}
                                    {% elif appointment.status == 'RESERVADO' %}
                                        <span class="badge bg-warning">Por confirmar</span>
                                    {% else %}
                                        <span class="badge bg-secondary">{{ appointment.get_status_display }}</span>
                                    {% endif %}
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm" role="group">
                                        {% if appointment.status == 'RESERVADO' %}
                                        <form method="post" action="{% url 'appointment_confirm' appointment.id %}" style="display:inline;">
                                            {% csrf_token %}
                                            <button type="submit" class="btn btn-success btn-sm" title="Confirmar">
                                                <i class="bi bi-check-circle"></i>
                                            </button>
                                        </form>
                                        {% endif %}
                                        {% if appointment.status == 'CONFIRMADO' and not appointment.checked_in_at %}
                                        <form method="post" action="{% url 'appointment_checkin' appointment.id %}" style="display:inline;">
                                            {% csrf_token %}
                                            <button type="submit" class="btn btn-info btn-sm" title="Check-in">
                                                <i class="bi bi-person-check"></i>
                                            </button>
                                        </form>
                                        {% endif %}
                                        <a href="{% url 'appointment_detail' appointment.id %}" class="btn btn-primary btn-sm" title="Ver detalles">
                                            <i class="bi bi-eye"></i>
                                        </a>
                                    </div>
                                </td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="5" class="text-center">No hay citas programadas para hoy</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Acciones Rápidas</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="{% url 'appointment_search' %}" class="btn btn-primary">
                        <i class="bi bi-search"></i> Buscar Horarios
                    </a>
                    <a href="{% url 'patient_create' %}" class="btn btn-success">
                        <i class="bi bi-person-plus"></i> Nuevo Paciente
                    </a>
                    <a href="{% url 'patient_list' %}" class="btn btn-info">
                        <i class="bi bi-people"></i> Lista de Pacientes
                    </a>
                    <a href="{% url 'calendar' %}" class="btn btn-warning">
                        <i class="bi bi-calendar-week"></i> Calendario
                    </a>
                    <a href="{% url 'appointment_list' %}" class="btn btn-secondary">
                        <i class="bi bi-list-ul"></i> Todas las Citas
                    </a>
                </div>
            </div>
        </div>
        
        <div class="card mt-3">
            <div class="card-header">
                <h5 class="mb-0">Pendientes de Confirmación</h5>
            </div>
            <div class="card-body">
                <div class="list-group">
                    {% for appointment in pending_confirmations|slice:":5" %}
                    <a href="{% url 'appointment_detail' appointment.id %}" class="list-group-item list-group-item-action">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">{{ appointment.patient.user.get_full_name }}</h6>
                            <small>{{ appointment.slot.start_dt|date:"d/m H:i" }}</small>
                        </div>
                        <p class="mb-1">Dr. {{ appointment.slot.doctor.user.get_full_name }}</p>
                    </a>
                    {% empty %}
                    <p class="text-muted text-center">No hay citas pendientes</p>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    # Dashboard Médico
    'templates/accounts/dashboard_doctor.html': '''{% extends 'base.html' %}
{% block title %}Dashboard - Médico{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Mi Panel Médico</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <span class="badge bg-primary">{{ doctor.specialty.name }}</span>
    </div>
</div>

<div class="row">
    <div class="col-md-4">
        <div class="card stat-card primary">
            <div class="card-body">
                <h5 class="card-title">Citas de Hoy</h5>
                <h2 class="text-primary">{{ today_appointments.count }}</h2>
                <p class="text-muted mb-0">Pacientes programados</p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card stat-card warning">
            <div class="card-body">
                <h5 class="card-title">Esta Semana</h5>
                <h2 class="text-warning">{{ week_appointments }}</h2>
                <p class="text-muted mb-0">Total de citas</p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card stat-card info">
            <div class="card-body">
                <h5 class="card-title">Pendientes</h5>
                <h2 class="text-info">{{ pending_patients }}</h2>
                <p class="text-muted mb-0">Por atender</p>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Agenda del Día</h5>
                <a href="{% url 'doctor_schedule' %}" class="btn btn-sm btn-outline-primary">Ver semana completa</a>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Hora</th>
                                <th>Paciente</th>
                                <th>Edad</th>
                                <th>Tipo</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for appointment in today_appointments %}
                            <tr>
                                <td>{{ appointment.slot.start_dt|date:"H:i" }}</td>
                                <td>
                                    <strong>{{ appointment.patient.user.get_full_name }}</strong><br>
                                    <small class="text-muted">{{ appointment.patient.user.document_id }}</small>
                                </td>
                                <td>
                                    {% load filters %}
                                    {{ appointment.patient.birthdate|age }} años
                                </td>
                                <td>Consulta</td>
                                <td>
                                    {% if appointment.status == 'ATENDIDO' %}
                                        <span class="badge bg-success">Atendido</span>
                                    {% elif appointment.checked_in_at %}
                                        <span class="badge bg-info">En espera</span>
                                    {% elif appointment.status == 'CONFIRMADO' %}
                                        <span class="badge bg-primary">Confirmado</span>
                                    {% else %}
                                        <span class="badge bg-warning">{{ appointment.get_status_display }}</span>
                                    {% endif %}
                                </td>
                                <td>
                                    {% if appointment.status != 'ATENDIDO' %}
                                    <form method="post" action="{% url 'appointment_attend' appointment.id %}" style="display:inline;">
                                        {% csrf_token %}
                                        <button type="submit" class="btn btn-success btn-sm" title="Marcar como atendido">
                                            <i class="bi bi-check-circle"></i> Atender
                                        </button>
                                    </form>
                                    {% endif %}
                                    <a href="{% url 'appointment_detail' appointment.id %}" class="btn btn-info btn-sm">
                                        <i class="bi bi-eye"></i> Ver
                                    </a>
                                </td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="6" class="text-center">No hay citas programadas para hoy</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Accesos Directos</h5>
            </div>
            <div class="card-body">
                <div class="list-group">
                    <a href="{% url 'doctor_schedule' %}" class="list-group-item list-group-item-action">
                        <i class="bi bi-calendar3"></i> Mi agenda completa
                    </a>
                    <a href="{% url 'doctor_patients' %}" class="list-group-item list-group-item-action">
                        <i class="bi bi-people"></i> Mis pacientes
                    </a>
                    <a href="{% url 'profile' %}" class="list-group-item list-group-item-action">
                        <i class="bi bi-person"></i> Mi perfil
                    </a>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Resumen de la Semana</h5>
            </div>
            <div class="card-body">
                <canvas id="weekChart" height="150"></canvas>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx = document.getElementById('weekChart').getContext('2d');
const weekChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
        datasets: [{
            label: 'Citas programadas',
            data: [8, 10, 7, 12, 9],
            backgroundColor: 'rgba(13, 110, 253, 0.5)',
            borderColor: 'rgba(13, 110, 253, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
</script>
{% endblock %}
''',

    # Dashboard Paciente
    'templates/accounts/dashboard_patient.html': '''{% extends 'base.html' %}
{% block title %}Mi Panel - Paciente{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Bienvenido, {{ user.get_full_name|default:user.username }}</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <a href="{% url 'appointment_search' %}" class="btn btn-primary">
            <i class="bi bi-calendar-plus"></i> Nueva Cita
        </a>
    </div>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Mis Próximas Citas</h5>
            </div>
            <div class="card-body">
                {% if upcoming_appointments %}
                <div class="list-group">
                    {% for appointment in upcoming_appointments %}
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">
                                <i class="bi bi-calendar-check"></i> 
                                {{ appointment.slot.start_dt|date:"l, d \d\e F" }}
                            </h5>
                            <span class="badge bg-{{ appointment.status|lower }} rounded-pill">
                                {{ appointment.get_status_display }}
                            </span>
                        </div>
                        <div class="row mt-2">
                            <div class="col-md-6">
                                <p class="mb-1">
                                    <strong>Hora:</strong> {{ appointment.slot.start_dt|date:"H:i" }}<br>
                                    <strong>Médico:</strong> Dr. {{ appointment.slot.doctor.user.get_full_name }}<br>
                                    <strong>Especialidad:</strong> {{ appointment.slot.doctor.specialty.name }}
                                </p>
                            </div>
                            <div class="col-md-6">
                                <p class="mb-1">
                                    <strong>Sede:</strong> {{ appointment.slot.location.name }}<br>
                                    <strong>Dirección:</strong> {{ appointment.slot.location.address }}
                                </p>
                            </div>
                        </div>
                        <div class="mt-2">
                            <a href="{% url 'appointment_detail' appointment.id %}" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-eye"></i> Ver detalles
                            </a>
                            {% if appointment.status in 'RESERVADO,CONFIRMADO' %}
                            <a href="{% url 'appointment_reschedule' appointment.id %}" class="btn btn-sm btn-outline-warning">
                                <i class="bi bi-calendar-x"></i> Reprogramar
                            </a>
                            <button type="button" class="btn btn-sm btn-outline-danger" data-bs-toggle="modal" data-bs-target="#cancelModal{{ appointment.id }}">
                                <i class="bi bi-x-circle"></i> Cancelar
                            </button>
                            {% endif %}
                        </div>
                    </div>
                    
                    <!-- Modal Cancelar -->
                    <div class="modal fade" id="cancelModal{{ appointment.id }}" tabindex="-1">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">Cancelar Cita</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <form method="post" action="{% url 'appointment_cancel' appointment.id %}">
                                    {% csrf_token %}
                                    <div class="modal-body">
                                        <p>¿Está seguro que desea cancelar esta cita?</p>
                                        <div class="mb-3">
                                            <label for="cancel_reason" class="form-label">Motivo de cancelación:</label>
                                            <textarea class="form-control" name="cancel_reason" rows="3" required></textarea>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                                        <button type="submit" class="btn btn-danger">Cancelar Cita</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> No tiene citas próximas programadas.
                    <a href="{% url 'appointment_search' %}" class="alert-link">Agendar una cita</a>
                </div>
                {% endif %}
            </div>
        </div>
        
        <div class="card mt-3">
            <div class="card-header">
                <h5 class="mb-0">Historial de Citas</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Fecha</th>
                                <th>Médico</th>
                                <th>Especialidad</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for appointment in past_appointments %}
                            <tr>
                                <td>{{ appointment.slot.start_dt|date:"d/m/Y" }}</td>
                                <td>Dr. {{ appointment.slot.doctor.user.get_full_name }}</td>
                                <td>{{ appointment.slot.doctor.specialty.name }}</td>
                                <td>
                                    <span class="badge bg-{{ appointment.status|lower }}">
                                        {{ appointment.get_status_display }}
                                    </span>
                                </td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="4" class="text-center">No hay historial de citas</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Mi Información</h5>
            </div>
            <div class="card-body">
                <p><strong>Nombre:</strong> {{ user.get_full_name }}</p>
                <p><strong>Documento:</strong> {{ user.document_id }}</p>
                <p><strong>Email:</strong> {{ user.email }}</p>
                <p><strong>Teléfono:</strong> {{ user.phone }}</p>
                {% if patient %}
                <p><strong>Fecha de nacimiento:</strong> {{ patient.birthdate|date:"d/m/Y" }}</p>
                <p><strong>Aseguradora:</strong> {{ patient.insurance|default:"No especificada" }}</p>
                {% endif %}
                <hr>
                <a href="{% url 'profile' %}" class="btn btn-outline-primary btn-sm">
                    <i class="bi bi-pencil"></i> Actualizar datos
                </a>
            </div>
        </div>
        
        <div class="card mt-3">
            <div class="card-header">
                <h5 class="mb-0">Resumen</h5>
            </div>
            <div class="card-body">
                <div class="row text-center">
                    <div class="col-6">
                        <h3 class="text-primary">{{ total_appointments }}</h3>
                        <small class="text-muted">Citas totales</small>
                    </div>
                    <div class="col-6">
                        <h3 class="text-success">{{ upcoming_appointments.count }}</h3>
                        <small class="text-muted">Próximas</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    # Profile
    'templates/accounts/profile.html': '''{% extends 'base.html' %}
{% block title %}Mi Perfil{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Mi Perfil</h1>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Información Personal</h5>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="first_name" class="form-label">Nombre</label>
                            <input type="text" class="form-control" id="first_name" name="first_name" value="{{ user.first_name }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="last_name" class="form-label">Apellido</label>
                            <input type="text" class="form-control" id="last_name" name="last_name" value="{{ user.last_name }}" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" class="form-control" id="email" name="email" value="{{ user.email }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="phone" class="form-label">Teléfono</label>
                            <input type="tel" class="form-control" id="phone" name="phone" value="{{ user.phone }}">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="username" class="form-label">Usuario</label>
                            <input type="text" class="form-control" id="username" value="{{ user.username }}" disabled>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="document_id" class="form-label">Documento</label>
                            <input type="text" class="form-control" id="document_id" value="{{ user.document_id }}" disabled>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-save"></i> Guardar Cambios
                    </button>
                </form>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Información de la Cuenta</h5>
            </div>
            <div class="card-body">
                <p><strong>Tipo de usuario:</strong> <span class="badge bg-primary">{{ user.get_role_display }}</span></p>
                <p><strong>Usuario desde:</strong> {{ user.date_joined|date:"d/m/Y" }}</p>
                <p><strong>Último acceso:</strong> {{ user.last_login|date:"d/m/Y H:i" }}</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
}

# Crear todos los templates
for filepath, content in templates.items():
    # Crear directorio si no existe
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    
    # Escribir archivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filepath}")

print("\nAll templates created successfully!")