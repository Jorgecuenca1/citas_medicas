import os

templates = {
    # Appointments Templates
    'templates/appointments/appointment_list.html': '''{% extends 'base.html' %}
{% block title %}Lista de Citas{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Gestión de Citas</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <a href="{% url 'appointment_search' %}" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Nueva Cita
        </a>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <form method="get" class="row g-3 mb-3">
            <div class="col-md-2">
                <select name="status" class="form-select">
                    <option value="">Todos los estados</option>
                    {% for status_code, status_name in statuses %}
                    <option value="{{ status_code }}" {% if request.GET.status == status_code %}selected{% endif %}>
                        {{ status_name }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <select name="doctor" class="form-select">
                    <option value="">Todos los médicos</option>
                    {% for doctor in doctors %}
                    <option value="{{ doctor.id }}" {% if request.GET.doctor == doctor.id|stringformat:"s" %}selected{% endif %}>
                        Dr. {{ doctor.user.get_full_name }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-2">
                <input type="date" name="date_from" class="form-control" value="{{ request.GET.date_from }}" placeholder="Desde">
            </div>
            <div class="col-md-2">
                <input type="date" name="date_to" class="form-control" value="{{ request.GET.date_to }}" placeholder="Hasta">
            </div>
            <div class="col-md-2">
                <button type="submit" class="btn btn-primary w-100">
                    <i class="bi bi-search"></i> Filtrar
                </button>
            </div>
            <div class="col-md-1">
                <a href="{% url 'appointment_list' %}" class="btn btn-secondary w-100">
                    <i class="bi bi-x"></i>
                </a>
            </div>
        </form>

        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Fecha/Hora</th>
                        <th>Paciente</th>
                        <th>Médico</th>
                        <th>Sede</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {% for appointment in appointments %}
                    <tr>
                        <td>#{{ appointment.id }}</td>
                        <td>{{ appointment.slot.start_dt|date:"d/m/Y H:i" }}</td>
                        <td>{{ appointment.patient.user.get_full_name }}</td>
                        <td>Dr. {{ appointment.slot.doctor.user.get_full_name }}</td>
                        <td>{{ appointment.slot.location.name }}</td>
                        <td>
                            {% if appointment.status == 'RESERVADO' %}
                                <span class="badge bg-warning">Reservado</span>
                            {% elif appointment.status == 'CONFIRMADO' %}
                                <span class="badge bg-success">Confirmado</span>
                            {% elif appointment.status == 'ATENDIDO' %}
                                <span class="badge bg-primary">Atendido</span>
                            {% elif appointment.status == 'CANCELADO_PAC' or appointment.status == 'CANCELADO_CLIN' %}
                                <span class="badge bg-danger">Cancelado</span>
                            {% else %}
                                <span class="badge bg-secondary">{{ appointment.get_status_display }}</span>
                            {% endif %}
                        </td>
                        <td>
                            <a href="{% url 'appointment_detail' appointment.id %}" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-eye"></i>
                            </a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="7" class="text-center">No se encontraron citas</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        {% if appointments.has_other_pages %}
        <nav>
            <ul class="pagination justify-content-center">
                {% if appointments.has_previous %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ appointments.previous_page_number }}">Anterior</a>
                    </li>
                {% endif %}
                
                {% for num in appointments.paginator.page_range %}
                    {% if appointments.number == num %}
                        <li class="page-item active"><span class="page-link">{{ num }}</span></li>
                    {% else %}
                        <li class="page-item"><a class="page-link" href="?page={{ num }}">{{ num }}</a></li>
                    {% endif %}
                {% endfor %}
                
                {% if appointments.has_next %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ appointments.next_page_number }}">Siguiente</a>
                    </li>
                {% endif %}
            </ul>
        </nav>
        {% endif %}
    </div>
</div>
{% endblock %}
''',

    'templates/appointments/appointment_search.html': '''{% extends 'base.html' %}
{% block title %}Buscar Horarios Disponibles{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Buscar Horarios Disponibles</h1>
</div>

<div class="card">
    <div class="card-header">
        <h5 class="mb-0">Criterios de Búsqueda</h5>
    </div>
    <div class="card-body">
        <form method="post">
            {% csrf_token %}
            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="specialty" class="form-label">Especialidad</label>
                    <select class="form-select" id="specialty" name="specialty" onchange="loadDoctors()">
                        <option value="">Todas las especialidades</option>
                        {% for specialty in specialties %}
                        <option value="{{ specialty.id }}">{{ specialty.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="doctor" class="form-label">Médico</label>
                    <select class="form-select" id="doctor" name="doctor">
                        <option value="">Cualquier médico</option>
                    </select>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="location" class="form-label">Sede</label>
                    <select class="form-select" id="location" name="location">
                        <option value="">Todas las sedes</option>
                        {% for location in locations %}
                        <option value="{{ location.id }}">{{ location.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="date_from" class="form-label">Desde</label>
                    <input type="date" class="form-control" id="date_from" name="date_from" min="{{ today|date:'Y-m-d' }}" required>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="date_to" class="form-label">Hasta</label>
                    <input type="date" class="form-control" id="date_to" name="date_to">
                </div>
                <div class="col-md-4 mb-3">
                    <label for="appointment_type" class="form-label">Tipo de Cita</label>
                    <select class="form-select" id="appointment_type" name="appointment_type">
                        {% for type in appointment_types %}
                        <option value="{{ type.id }}">{{ type.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <button type="submit" class="btn btn-primary">
                <i class="bi bi-search"></i> Buscar Horarios
            </button>
        </form>
    </div>
</div>

{% if search_performed %}
<div class="card mt-4">
    <div class="card-header">
        <h5 class="mb-0">Horarios Disponibles</h5>
    </div>
    <div class="card-body">
        {% if slots %}
        <div class="row">
            {% for slot in slots %}
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="bi bi-calendar-check"></i> 
                            {{ slot.start_dt|date:"l, d \\d\\e F" }}
                        </h6>
                        <p class="card-text">
                            <strong>Hora:</strong> {{ slot.start_dt|date:"H:i" }} - {{ slot.end_dt|date:"H:i" }}<br>
                            <strong>Médico:</strong> Dr. {{ slot.doctor.user.get_full_name }}<br>
                            <strong>Especialidad:</strong> {{ slot.doctor.specialty.name }}<br>
                            <strong>Sede:</strong> {{ slot.location.name }}
                        </p>
                        <a href="{% url 'appointment_book' slot.id %}" class="btn btn-success btn-sm w-100">
                            <i class="bi bi-check-circle"></i> Reservar
                        </a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="alert alert-warning">
            <i class="bi bi-exclamation-triangle"></i> No se encontraron horarios disponibles con los criterios seleccionados.
        </div>
        {% endif %}
    </div>
</div>
{% endif %}

<script>
function loadDoctors() {
    const specialtyId = document.getElementById('specialty').value;
    const doctorSelect = document.getElementById('doctor');
    
    if (!specialtyId) {
        doctorSelect.innerHTML = '<option value="">Cualquier médico</option>';
        return;
    }
    
    fetch(`/appointments/api/doctors-by-specialty/?specialty_id=${specialtyId}`)
        .then(response => response.json())
        .then(data => {
            doctorSelect.innerHTML = '<option value="">Cualquier médico</option>';
            data.forEach(doctor => {
                const option = document.createElement('option');
                option.value = doctor.id;
                option.textContent = `Dr. ${doctor.user__first_name} ${doctor.user__last_name}`;
                doctorSelect.appendChild(option);
            });
        });
}
</script>
{% endblock %}
''',

    'templates/appointments/appointment_detail.html': '''{% extends 'base.html' %}
{% block title %}Detalle de Cita #{{ appointment.id }}{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Cita #{{ appointment.id }}</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        {% if appointment.status == 'RESERVADO' %}
        <form method="post" action="{% url 'appointment_confirm' appointment.id %}" style="display:inline;">
            {% csrf_token %}
            <button type="submit" class="btn btn-success me-2">
                <i class="bi bi-check-circle"></i> Confirmar
            </button>
        </form>
        {% endif %}
        
        {% if appointment.status in 'RESERVADO,CONFIRMADO' %}
        <a href="{% url 'appointment_reschedule' appointment.id %}" class="btn btn-warning me-2">
            <i class="bi bi-calendar-x"></i> Reprogramar
        </a>
        <button type="button" class="btn btn-danger" data-bs-toggle="modal" data-bs-target="#cancelModal">
            <i class="bi bi-x-circle"></i> Cancelar
        </button>
        {% endif %}
        
        {% if appointment.status == 'CONFIRMADO' and not appointment.checked_in_at %}
        <form method="post" action="{% url 'appointment_checkin' appointment.id %}" style="display:inline;">
            {% csrf_token %}
            <button type="submit" class="btn btn-info ms-2">
                <i class="bi bi-person-check"></i> Check-in
            </button>
        </form>
        {% endif %}
        
        {% if appointment.checked_in_at and appointment.status != 'ATENDIDO' %}
        <form method="post" action="{% url 'appointment_attend' appointment.id %}" style="display:inline;">
            {% csrf_token %}
            <button type="submit" class="btn btn-primary ms-2">
                <i class="bi bi-check-square"></i> Marcar Atendido
            </button>
        </form>
        {% endif %}
    </div>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Información de la Cita</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Estado:</strong> 
                            {% if appointment.status == 'RESERVADO' %}
                                <span class="badge bg-warning">Reservado</span>
                            {% elif appointment.status == 'CONFIRMADO' %}
                                <span class="badge bg-success">Confirmado</span>
                            {% elif appointment.status == 'ATENDIDO' %}
                                <span class="badge bg-primary">Atendido</span>
                            {% else %}
                                <span class="badge bg-secondary">{{ appointment.get_status_display }}</span>
                            {% endif %}
                        </p>
                        <p><strong>Fecha:</strong> {{ appointment.slot.start_dt|date:"l, d \\d\\e F \\d\\e Y" }}</p>
                        <p><strong>Hora:</strong> {{ appointment.slot.start_dt|date:"H:i" }} - {{ appointment.slot.end_dt|date:"H:i" }}</p>
                        <p><strong>Sede:</strong> {{ appointment.slot.location.name }}</p>
                        <p><strong>Dirección:</strong> {{ appointment.slot.location.address }}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Médico:</strong> Dr. {{ appointment.slot.doctor.user.get_full_name }}</p>
                        <p><strong>Especialidad:</strong> {{ appointment.slot.doctor.specialty.name }}</p>
                        <p><strong>Reservada:</strong> {{ appointment.booked_at|date:"d/m/Y H:i" }}</p>
                        {% if appointment.confirmed_at %}
                        <p><strong>Confirmada:</strong> {{ appointment.confirmed_at|date:"d/m/Y H:i" }}</p>
                        {% endif %}
                        {% if appointment.checked_in_at %}
                        <p><strong>Check-in:</strong> {{ appointment.checked_in_at|date:"d/m/Y H:i" }}</p>
                        {% endif %}
                    </div>
                </div>
                {% if appointment.notes %}
                <hr>
                <p><strong>Notas:</strong></p>
                <p>{{ appointment.notes }}</p>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Información del Paciente</h5>
            </div>
            <div class="card-body">
                <p><strong>Nombre:</strong> {{ appointment.patient.user.get_full_name }}</p>
                <p><strong>Documento:</strong> {{ appointment.patient.user.document_id }}</p>
                <p><strong>Teléfono:</strong> {{ appointment.patient.user.phone }}</p>
                <p><strong>Email:</strong> {{ appointment.patient.user.email }}</p>
                <p><strong>Edad:</strong> 
                    {% load filters %}
                    {{ appointment.patient.birthdate|age }} años
                </p>
                <p><strong>Aseguradora:</strong> {{ appointment.patient.insurance|default:"No especificada" }}</p>
                <hr>
                <a href="{% url 'patient_detail' appointment.patient.id %}" class="btn btn-outline-primary btn-sm">
                    <i class="bi bi-person"></i> Ver perfil completo
                </a>
            </div>
        </div>
    </div>
</div>

<!-- Modal Cancelar -->
<div class="modal fade" id="cancelModal" tabindex="-1">
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
{% endblock %}
''',

    'templates/appointments/appointment_book.html': '''{% extends 'base.html' %}
{% block title %}Reservar Cita{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Reservar Cita</h1>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Detalles del Horario</h5>
            </div>
            <div class="card-body">
                <p><strong>Fecha:</strong> {{ slot.start_dt|date:"l, d \\d\\e F \\d\\e Y" }}</p>
                <p><strong>Hora:</strong> {{ slot.start_dt|date:"H:i" }} - {{ slot.end_dt|date:"H:i" }}</p>
                <p><strong>Médico:</strong> Dr. {{ slot.doctor.user.get_full_name }}</p>
                <p><strong>Especialidad:</strong> {{ slot.doctor.specialty.name }}</p>
                <p><strong>Sede:</strong> {{ slot.location.name }}</p>
                <p><strong>Dirección:</strong> {{ slot.location.address }}</p>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Seleccionar Paciente</h5>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="patient_id" class="form-label">Paciente</label>
                        <select class="form-select" id="patient_id" name="patient_id" required>
                            <option value="">Seleccione un paciente</option>
                            {% for patient in patients %}
                            <option value="{{ patient.id }}">
                                {{ patient.user.get_full_name }} - {{ patient.user.document_id }}
                            </option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="notes" class="form-label">Notas (opcional)</label>
                        <textarea class="form-control" id="notes" name="notes" rows="3"></textarea>
                    </div>
                    <button type="submit" class="btn btn-success">
                        <i class="bi bi-check-circle"></i> Confirmar Reserva
                    </button>
                    <a href="{% url 'appointment_search' %}" class="btn btn-secondary">
                        <i class="bi bi-arrow-left"></i> Volver
                    </a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    'templates/appointments/calendar.html': '''{% extends 'base.html' %}
{% block title %}Calendario de Citas{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Calendario de Citas</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <div class="btn-group me-2">
            <a href="?view=day&date={{ current_date|date:'Y-m-d' }}" class="btn btn-sm btn-outline-secondary {% if view_type == 'day' %}active{% endif %}">Día</a>
            <a href="?view=week&date={{ current_date|date:'Y-m-d' }}" class="btn btn-sm btn-outline-secondary {% if view_type == 'week' %}active{% endif %}">Semana</a>
            <a href="?view=month&date={{ current_date|date:'Y-m-d' }}" class="btn btn-sm btn-outline-secondary {% if view_type == 'month' %}active{% endif %}">Mes</a>
        </div>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <div id="calendar"></div>
    </div>
</div>

<link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.css' rel='stylesheet' />
<script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js'></script>
<script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/locales/es.js'></script>

<script>
document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: '{{ view_type }}View',
        locale: 'es',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: [
            {% for appointment in appointments %}
            {
                title: '{{ appointment.patient.user.get_full_name }}',
                start: '{{ appointment.slot.start_dt|date:"c" }}',
                end: '{{ appointment.slot.end_dt|date:"c" }}',
                url: '{% url "appointment_detail" appointment.id %}',
                {% if appointment.status == 'CONFIRMADO' %}
                color: '#28a745',
                {% elif appointment.status == 'RESERVADO' %}
                color: '#ffc107',
                {% elif appointment.status == 'ATENDIDO' %}
                color: '#007bff',
                {% else %}
                color: '#6c757d',
                {% endif %}
            },
            {% endfor %}
        ],
        eventClick: function(info) {
            info.jsEvent.preventDefault();
            window.location.href = info.event.url;
        }
    });
    calendar.render();
});
</script>
{% endblock %}
''',

    # Patients Templates
    'templates/patients/patient_list.html': '''{% extends 'base.html' %}
{% block title %}Lista de Pacientes{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Pacientes</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <a href="{% url 'patient_create' %}" class="btn btn-primary">
            <i class="bi bi-person-plus"></i> Nuevo Paciente
        </a>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <form method="get" class="mb-3">
            <div class="input-group">
                <input type="text" name="search" class="form-control" placeholder="Buscar por nombre, documento o email..." value="{{ search }}">
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-search"></i> Buscar
                </button>
                {% if search %}
                <a href="{% url 'patient_list' %}" class="btn btn-secondary">
                    <i class="bi bi-x"></i> Limpiar
                </a>
                {% endif %}
            </div>
        </form>

        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Documento</th>
                        <th>Nombre</th>
                        <th>Teléfono</th>
                        <th>Email</th>
                        <th>Edad</th>
                        <th>Aseguradora</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {% for patient in patients %}
                    <tr>
                        <td>{{ patient.user.document_id }}</td>
                        <td>{{ patient.user.get_full_name }}</td>
                        <td>{{ patient.user.phone }}</td>
                        <td>{{ patient.user.email }}</td>
                        <td>
                            {% load filters %}
                            {{ patient.birthdate|age }} años
                        </td>
                        <td>{{ patient.insurance|default:"-" }}</td>
                        <td>
                            <a href="{% url 'patient_detail' patient.id %}" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{% url 'patient_update' patient.id %}" class="btn btn-sm btn-outline-secondary">
                                <i class="bi bi-pencil"></i>
                            </a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="7" class="text-center">No se encontraron pacientes</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
''',

    'templates/patients/patient_form.html': '''{% extends 'base.html' %}
{% block title %}{% if is_update %}Actualizar{% else %}Nuevo{% endif %} Paciente{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">{% if is_update %}Actualizar{% else %}Nuevo{% endif %} Paciente</h1>
</div>

<div class="card">
    <div class="card-body">
        <form method="post">
            {% csrf_token %}
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="first_name" class="form-label">Nombre</label>
                    <input type="text" class="form-control" id="first_name" name="first_name" 
                           value="{% if is_update %}{{ patient.user.first_name }}{% endif %}" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="last_name" class="form-label">Apellido</label>
                    <input type="text" class="form-control" id="last_name" name="last_name" 
                           value="{% if is_update %}{{ patient.user.last_name }}{% endif %}" required>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="document_id" class="form-label">Documento de Identidad</label>
                    <input type="text" class="form-control" id="document_id" name="document_id" 
                           value="{% if is_update %}{{ patient.user.document_id }}{% endif %}" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="birthdate" class="form-label">Fecha de Nacimiento</label>
                    <input type="date" class="form-control" id="birthdate" name="birthdate" 
                           value="{% if is_update %}{{ patient.birthdate|date:'Y-m-d' }}{% endif %}" required>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="gender" class="form-label">Género</label>
                    <select class="form-select" id="gender" name="gender" required>
                        <option value="">Seleccione...</option>
                        <option value="M" {% if is_update and patient.gender == 'M' %}selected{% endif %}>Masculino</option>
                        <option value="F" {% if is_update and patient.gender == 'F' %}selected{% endif %}>Femenino</option>
                        <option value="O" {% if is_update and patient.gender == 'O' %}selected{% endif %}>Otro</option>
                    </select>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="phone" class="form-label">Teléfono</label>
                    <input type="tel" class="form-control" id="phone" name="phone" 
                           value="{% if is_update %}{{ patient.user.phone }}{% endif %}" required>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email" 
                           value="{% if is_update %}{{ patient.user.email }}{% endif %}" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="insurance" class="form-label">Aseguradora</label>
                    <input type="text" class="form-control" id="insurance" name="insurance" 
                           value="{% if is_update %}{{ patient.insurance }}{% endif %}">
                </div>
            </div>
            
            {% if not is_update %}
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="username" class="form-label">Usuario</label>
                    <input type="text" class="form-control" id="username" name="username" required>
                    <small class="text-muted">Este será el usuario para iniciar sesión</small>
                </div>
            </div>
            {% endif %}
            
            <div class="mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="consent" name="consent" 
                           {% if is_update and patient.consent_given_at %}checked{% endif %}>
                    <label class="form-check-label" for="consent">
                        Acepto el tratamiento de mis datos personales
                    </label>
                </div>
            </div>
            
            <button type="submit" class="btn btn-primary">
                <i class="bi bi-save"></i> {% if is_update %}Actualizar{% else %}Crear{% endif %} Paciente
            </button>
            <a href="{% url 'patient_list' %}" class="btn btn-secondary">
                <i class="bi bi-arrow-left"></i> Volver
            </a>
        </form>
    </div>
</div>
{% endblock %}
''',

    # Create a template filter for age calculation
    'templates/templatetags/__init__.py': '',
    'templates/templatetags/filters.py': '''from django import template
from datetime import date

register = template.Library()

@register.filter
def age(birthdate):
    if not birthdate:
        return ""
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age
''',
}

# Create all templates
for filepath, content in templates.items():
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filepath}")

print("\nAll remaining templates created!")