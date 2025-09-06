import os

# Templates faltantes
templates = {
    # Doctors templates
    'templates/doctors/doctor_list.html': '''{% extends 'base.html' %}
{% block title %}Lista de Médicos{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Médicos</h1>
</div>

<div class="card">
    <div class="card-body">
        <div class="row">
            {% for doctor in doctors %}
            <div class="col-md-4 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="bi bi-person-badge"></i> Dr. {{ doctor.user.get_full_name }}
                        </h5>
                        <h6 class="card-subtitle mb-2 text-muted">{{ doctor.specialty.name }}</h6>
                        <p class="card-text">
                            <small><strong>Licencia:</strong> {{ doctor.license_number }}</small><br>
                            <small><strong>Sedes:</strong> 
                                {% for location in doctor.locations.all %}
                                    {{ location.name }}{% if not forloop.last %}, {% endif %}
                                {% endfor %}
                            </small>
                        </p>
                        {% if doctor.bio %}
                        <p class="card-text">{{ doctor.bio|truncatewords:20 }}</p>
                        {% endif %}
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-{{ doctor.active|yesno:'success,danger' }}">
                                {{ doctor.active|yesno:'Activo,Inactivo' }}
                            </span>
                            <a href="{% url 'doctor_detail' doctor.id %}" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-eye"></i> Ver detalles
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            {% empty %}
            <div class="col-12">
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> No hay médicos registrados en el sistema.
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
''',

    'templates/doctors/doctor_detail.html': '''{% extends 'base.html' %}
{% block title %}Dr. {{ doctor.user.get_full_name }}{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Dr. {{ doctor.user.get_full_name }}</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <span class="badge bg-primary">{{ doctor.specialty.name }}</span>
        <span class="badge bg-{{ doctor.active|yesno:'success,danger' }} ms-2">
            {{ doctor.active|yesno:'Activo,Inactivo' }}
        </span>
    </div>
</div>

<div class="row">
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Información del Médico</h5>
            </div>
            <div class="card-body">
                <p><strong>Nombre completo:</strong> {{ doctor.user.get_full_name }}</p>
                <p><strong>Especialidad:</strong> {{ doctor.specialty.name }}</p>
                <p><strong>Licencia médica:</strong> {{ doctor.license_number }}</p>
                <p><strong>Email:</strong> {{ doctor.user.email }}</p>
                <p><strong>Teléfono:</strong> {{ doctor.user.phone|default:"No registrado" }}</p>
                <hr>
                <p><strong>Sedes de atención:</strong></p>
                <ul>
                    {% for location in doctor.locations.all %}
                    <li>{{ location.name }}</li>
                    {% empty %}
                    <li>No asignado a ninguna sede</li>
                    {% endfor %}
                </ul>
                {% if doctor.bio %}
                <hr>
                <p><strong>Biografía:</strong></p>
                <p>{{ doctor.bio }}</p>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Próximas Citas</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Fecha</th>
                                <th>Hora</th>
                                <th>Paciente</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for appointment in upcoming_appointments %}
                            <tr>
                                <td>{{ appointment.slot.start_dt|date:"d/m/Y" }}</td>
                                <td>{{ appointment.slot.start_dt|date:"H:i" }}</td>
                                <td>{{ appointment.patient.user.get_full_name }}</td>
                                <td>
                                    {% if appointment.status == 'CONFIRMADO' %}
                                        <span class="badge bg-success">Confirmado</span>
                                    {% elif appointment.status == 'RESERVADO' %}
                                        <span class="badge bg-warning">Reservado</span>
                                    {% else %}
                                        <span class="badge bg-secondary">{{ appointment.get_status_display }}</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="4" class="text-center">No hay citas programadas</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    'templates/doctors/doctor_schedule.html': '''{% extends 'base.html' %}
{% block title %}Mi Agenda - Dr. {{ doctor.user.get_full_name }}{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Mi Agenda Semanal</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <span class="text-muted">Semana del {{ week_start|date:"d/m" }} al {{ week_end|date:"d/m/Y" }}</span>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Hora</th>
                        <th>Lunes</th>
                        <th>Martes</th>
                        <th>Miércoles</th>
                        <th>Jueves</th>
                        <th>Viernes</th>
                        <th>Sábado</th>
                    </tr>
                </thead>
                <tbody>
                    {% for hour in "8,9,10,11,12,13,14,15,16,17,18"|make_list %}
                    <tr>
                        <td><strong>{{ hour }}:00</strong></td>
                        {% for day in "0,1,2,3,4,5"|make_list %}
                        <td>
                            {% for appointment in appointments %}
                                {% if appointment.slot.start_dt.hour == hour|add:0 and appointment.slot.start_dt.weekday == day|add:0 %}
                                <div class="alert alert-info p-1 mb-1">
                                    <small>
                                        <strong>{{ appointment.patient.user.get_full_name }}</strong><br>
                                        {{ appointment.slot.start_dt|date:"H:i" }}
                                        {% if appointment.status == 'ATENDIDO' %}
                                            <span class="badge bg-success">✓</span>
                                        {% endif %}
                                    </small>
                                </div>
                                {% endif %}
                            {% endfor %}
                        </td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<div class="card mt-3">
    <div class="card-header">
        <h5 class="mb-0">Detalle de Citas</h5>
    </div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Fecha/Hora</th>
                        <th>Paciente</th>
                        <th>Teléfono</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {% for appointment in appointments %}
                    <tr>
                        <td>{{ appointment.slot.start_dt|date:"d/m H:i" }}</td>
                        <td>{{ appointment.patient.user.get_full_name }}</td>
                        <td>{{ appointment.patient.user.phone }}</td>
                        <td>
                            {% if appointment.status == 'CONFIRMADO' %}
                                <span class="badge bg-success">Confirmado</span>
                            {% elif appointment.status == 'ATENDIDO' %}
                                <span class="badge bg-primary">Atendido</span>
                            {% else %}
                                <span class="badge bg-warning">{{ appointment.get_status_display }}</span>
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
                        <td colspan="5" class="text-center">No hay citas programadas esta semana</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
''',

    'templates/doctors/doctor_patients.html': '''{% extends 'base.html' %}
{% block title %}Mis Pacientes{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Mis Pacientes</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <span class="text-muted">Total: {{ patients.count }} pacientes</span>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Documento</th>
                        <th>Nombre</th>
                        <th>Edad</th>
                        <th>Teléfono</th>
                        <th>Email</th>
                        <th>Última cita</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {% for patient in patients %}
                    <tr>
                        <td>{{ patient.user.document_id }}</td>
                        <td>{{ patient.user.get_full_name }}</td>
                        <td>
                            {% load filters %}
                            {{ patient.birthdate|age }} años
                        </td>
                        <td>{{ patient.user.phone }}</td>
                        <td>{{ patient.user.email }}</td>
                        <td>-</td>
                        <td>
                            <a href="{% url 'patient_detail' patient.id %}" class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-eye"></i> Ver historial
                            </a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="7" class="text-center">No tiene pacientes registrados</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
''',

    # Patient detail and profile
    'templates/patients/patient_detail.html': '''{% extends 'base.html' %}
{% block title %}{{ patient.user.get_full_name }}{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">{{ patient.user.get_full_name }}</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <a href="{% url 'patient_update' patient.id %}" class="btn btn-outline-primary me-2">
            <i class="bi bi-pencil"></i> Editar
        </a>
        <a href="{% url 'appointment_search' %}" class="btn btn-primary">
            <i class="bi bi-calendar-plus"></i> Nueva Cita
        </a>
    </div>
</div>

<div class="row">
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Información Personal</h5>
            </div>
            <div class="card-body">
                <p><strong>Documento:</strong> {{ patient.user.document_id }}</p>
                <p><strong>Fecha de nacimiento:</strong> {{ patient.birthdate|date:"d/m/Y" }}</p>
                <p><strong>Edad:</strong> 
                    {% load filters %}
                    {{ patient.birthdate|age }} años
                </p>
                <p><strong>Género:</strong> {{ patient.get_gender_display }}</p>
                <p><strong>Teléfono:</strong> {{ patient.user.phone }}</p>
                <p><strong>Email:</strong> {{ patient.user.email }}</p>
                <p><strong>Aseguradora:</strong> {{ patient.insurance|default:"No especificada" }}</p>
                <p><strong>Consentimiento:</strong> 
                    {% if patient.consent_given_at %}
                        <span class="badge bg-success">Otorgado</span>
                    {% else %}
                        <span class="badge bg-warning">Pendiente</span>
                    {% endif %}
                </p>
            </div>
        </div>
        
        <div class="card mt-3">
            <div class="card-header">
                <h5 class="mb-0">Estadísticas</h5>
            </div>
            <div class="card-body">
                <div class="row text-center">
                    <div class="col-6">
                        <h3 class="text-primary">{{ upcoming_count }}</h3>
                        <small class="text-muted">Próximas citas</small>
                    </div>
                    <div class="col-6">
                        <h3 class="text-success">{{ past_count }}</h3>
                        <small class="text-muted">Citas pasadas</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Historial de Citas</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Fecha</th>
                                <th>Hora</th>
                                <th>Médico</th>
                                <th>Especialidad</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for appointment in appointments %}
                            <tr>
                                <td>{{ appointment.slot.start_dt|date:"d/m/Y" }}</td>
                                <td>{{ appointment.slot.start_dt|date:"H:i" }}</td>
                                <td>Dr. {{ appointment.slot.doctor.user.get_full_name }}</td>
                                <td>{{ appointment.slot.doctor.specialty.name }}</td>
                                <td>
                                    {% if appointment.status == 'CONFIRMADO' %}
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
                                        <i class="bi bi-eye"></i>
                                    </a>
                                </td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="6" class="text-center">No hay historial de citas</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    'templates/patients/patient_profile_form.html': '''{% extends 'base.html' %}
{% block title %}Completar Perfil de Paciente{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Completar mi Perfil de Paciente</h1>
</div>

<div class="card">
    <div class="card-body">
        <form method="post">
            {% csrf_token %}
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="birthdate" class="form-label">Fecha de Nacimiento</label>
                    <input type="date" class="form-control" id="birthdate" name="birthdate" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="gender" class="form-label">Género</label>
                    <select class="form-select" id="gender" name="gender" required>
                        <option value="">Seleccione...</option>
                        <option value="M">Masculino</option>
                        <option value="F">Femenino</option>
                        <option value="O">Otro</option>
                    </select>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="insurance" class="form-label">Aseguradora (opcional)</label>
                    <input type="text" class="form-control" id="insurance" name="insurance">
                </div>
            </div>
            
            <div class="mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="consent" name="consent" required>
                    <label class="form-check-label" for="consent">
                        Acepto el tratamiento de mis datos personales de acuerdo con la política de privacidad
                    </label>
                </div>
            </div>
            
            <button type="submit" class="btn btn-primary">
                <i class="bi bi-save"></i> Guardar Perfil
            </button>
        </form>
    </div>
</div>
{% endblock %}
''',

    # Reports templates
    'templates/reports/dashboard.html': '''{% extends 'base.html' %}
{% block title %}Dashboard de Reportes{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Dashboard de Reportes</h1>
</div>

<div class="row">
    <div class="col-md-3">
        <div class="card stat-card primary">
            <div class="card-body">
                <h5 class="card-title">Citas del Mes</h5>
                <h2 class="text-primary">{{ total_appointments_month }}</h2>
                <p class="text-muted mb-0">Total programadas</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card success">
            <div class="card-body">
                <h5 class="card-title">Pacientes</h5>
                <h2 class="text-success">{{ total_patients }}</h2>
                <p class="text-muted mb-0">Total registrados</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card warning">
            <div class="card-body">
                <h5 class="card-title">Tasa Cancelación</h5>
                <h2 class="text-warning">{{ cancellation_rate }}%</h2>
                <p class="text-muted mb-0">Este mes</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card danger">
            <div class="card-body">
                <h5 class="card-title">No-Show</h5>
                <h2 class="text-danger">{{ no_show_rate }}%</h2>
                <p class="text-muted mb-0">Este mes</p>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Reportes Disponibles</h5>
            </div>
            <div class="card-body">
                <div class="list-group">
                    <a href="{% url 'appointments_report' %}" class="list-group-item list-group-item-action">
                        <i class="bi bi-calendar-check"></i> Reporte de Citas
                        <small class="text-muted float-end">Ver detalles →</small>
                    </a>
                    <a href="{% url 'occupancy_report' %}" class="list-group-item list-group-item-action">
                        <i class="bi bi-graph-up"></i> Reporte de Ocupación
                        <small class="text-muted float-end">Ver detalles →</small>
                    </a>
                    <a href="{% url 'cancellations_report' %}" class="list-group-item list-group-item-action">
                        <i class="bi bi-x-circle"></i> Reporte de Cancelaciones
                        <small class="text-muted float-end">Ver detalles →</small>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    # Appointment reschedule
    'templates/appointments/appointment_reschedule.html': '''{% extends 'base.html' %}
{% block title %}Reprogramar Cita{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">Reprogramar Cita #{{ appointment.id }}</h1>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-warning text-white">
                <h5 class="mb-0">Cita Actual</h5>
            </div>
            <div class="card-body">
                <p><strong>Fecha:</strong> {{ appointment.slot.start_dt|date:"d/m/Y" }}</p>
                <p><strong>Hora:</strong> {{ appointment.slot.start_dt|date:"H:i" }}</p>
                <p><strong>Médico:</strong> Dr. {{ appointment.slot.doctor.user.get_full_name }}</p>
                <p><strong>Paciente:</strong> {{ appointment.patient.user.get_full_name }}</p>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0">Seleccionar Nueva Fecha</h5>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label class="form-label">Horarios disponibles del mismo médico:</label>
                        {% for slot in available_slots %}
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="new_slot_id" id="slot{{ slot.id }}" value="{{ slot.id }}">
                            <label class="form-check-label" for="slot{{ slot.id }}">
                                {{ slot.start_dt|date:"d/m/Y H:i" }} - {{ slot.end_dt|date:"H:i" }}
                            </label>
                        </div>
                        {% empty %}
                        <p class="text-muted">No hay horarios disponibles próximamente</p>
                        {% endfor %}
                    </div>
                    
                    {% if available_slots %}
                    <button type="submit" class="btn btn-success">
                        <i class="bi bi-check-circle"></i> Confirmar Reprogramación
                    </button>
                    {% endif %}
                    <a href="{% url 'appointment_detail' appointment.id %}" class="btn btn-secondary">
                        <i class="bi bi-arrow-left"></i> Cancelar
                    </a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
}

# Crear todos los templates faltantes
for filepath, content in templates.items():
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filepath}")

print("\nAll missing templates created successfully!")