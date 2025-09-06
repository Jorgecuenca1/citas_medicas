import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_appointments.settings')
django.setup()

from accounts.models import User
from core.models import Specialty, Location, Room
from doctors.models import Doctor
from patients.models import Patient
from appointments.models import AppointmentType
from availability.models import ScheduleTemplate, Holiday
from datetime import date, time, datetime
from django.utils import timezone

def create_seed_data():
    print("Creating seed data...")
    
    # Create specialties
    specialties = [
        {'code': 'MG', 'name': 'Medicina General'},
        {'code': 'PED', 'name': 'Pediatría'},
        {'code': 'GIN', 'name': 'Ginecología'},
        {'code': 'CAR', 'name': 'Cardiología'},
        {'code': 'DER', 'name': 'Dermatología'},
        {'code': 'OFT', 'name': 'Oftalmología'},
        {'code': 'ORT', 'name': 'Ortopedia'},
        {'code': 'NEU', 'name': 'Neurología'},
    ]
    
    for spec_data in specialties:
        spec, created = Specialty.objects.get_or_create(**spec_data)
        if created:
            print(f"  Created specialty: {spec.name}")
    
    # Create locations
    locations = [
        {
            'name': 'Clínica Principal',
            'address': 'Calle 100 #15-20, Bogotá',
            'timezone': 'America/Bogota',
            'active': True
        },
        {
            'name': 'Sede Norte',
            'address': 'Av 19 #127-15, Bogotá',
            'timezone': 'America/Bogota',
            'active': True
        }
    ]
    
    for loc_data in locations:
        loc, created = Location.objects.get_or_create(
            name=loc_data['name'],
            defaults=loc_data
        )
        if created:
            print(f"  Created location: {loc.name}")
            
            # Create rooms for each location
            for i in range(1, 6):
                room, room_created = Room.objects.get_or_create(
                    location=loc,
                    name=f"Consultorio {i}",
                    defaults={'resource_tags': []}
                )
                if room_created:
                    print(f"    Created room: {room.name}")
    
    # Create appointment types
    appointment_types = [
        {'name': 'Consulta General', 'duration_min': 20, 'requires_room': True},
        {'name': 'Consulta Especialista', 'duration_min': 30, 'requires_room': True},
        {'name': 'Control', 'duration_min': 15, 'requires_room': True},
        {'name': 'Procedimiento', 'duration_min': 45, 'requires_room': True},
        {'name': 'Telemedicina', 'duration_min': 20, 'requires_room': False},
    ]
    
    for type_data in appointment_types:
        app_type, created = AppointmentType.objects.get_or_create(
            name=type_data['name'],
            defaults=type_data
        )
        if created:
            print(f"  Created appointment type: {app_type.name}")
    
    # Create sample users and profiles
    # Create reception user
    recep_user, created = User.objects.get_or_create(
        username='recepcion1',
        defaults={
            'email': 'recepcion@clinic.com',
            'first_name': 'María',
            'last_name': 'González',
            'role': 'RECEP',
            'phone': '3001234567',
            'document_id': '52123456'
        }
    )
    if created:
        recep_user.set_password('recep123')
        recep_user.save()
        print(f"  Created reception user: {recep_user.username}")
    
    # Create doctors
    doctors_data = [
        {
            'username': 'dr_rodriguez',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'email': 'crodriguez@clinic.com',
            'phone': '3009876543',
            'document_id': '79123456',
            'license': 'MP12345',
            'specialty': 'MG'
        },
        {
            'username': 'dra_martinez',
            'first_name': 'Ana',
            'last_name': 'Martínez',
            'email': 'amartinez@clinic.com',
            'phone': '3001112233',
            'document_id': '52987654',
            'license': 'MP54321',
            'specialty': 'PED'
        },
        {
            'username': 'dr_lopez',
            'first_name': 'Juan',
            'last_name': 'López',
            'email': 'jlopez@clinic.com',
            'phone': '3004445566',
            'document_id': '79456789',
            'license': 'MP67890',
            'specialty': 'CAR'
        }
    ]
    
    for doc_data in doctors_data:
        user, created = User.objects.get_or_create(
            username=doc_data['username'],
            defaults={
                'email': doc_data['email'],
                'first_name': doc_data['first_name'],
                'last_name': doc_data['last_name'],
                'role': 'MEDICO',
                'phone': doc_data['phone'],
                'document_id': doc_data['document_id']
            }
        )
        if created:
            user.set_password('doctor123')
            user.save()
            
            # Create doctor profile
            specialty = Specialty.objects.get(code=doc_data['specialty'])
            doctor, doc_created = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    'license_number': doc_data['license'],
                    'specialty': specialty,
                    'bio': f"Médico especialista con amplia experiencia.",
                    'active': True
                }
            )
            if doc_created:
                # Add locations to doctor
                doctor.locations.add(*Location.objects.filter(active=True))
                print(f"  Created doctor: Dr. {user.get_full_name()}")
                
                # Create schedule templates for doctor
                location = Location.objects.first()
                for weekday in range(5):  # Monday to Friday
                    template, tpl_created = ScheduleTemplate.objects.get_or_create(
                        doctor=doctor,
                        location=location,
                        weekday=weekday,
                        start_time=time(8, 0),
                        end_time=time(12, 0),
                        defaults={
                            'slot_every_min': 20,
                            'max_overbooking': 0
                        }
                    )
                    if tpl_created:
                        print(f"    Created morning schedule for {['Mon','Tue','Wed','Thu','Fri'][weekday]}")
                    
                    # Afternoon schedule
                    template2, tpl2_created = ScheduleTemplate.objects.get_or_create(
                        doctor=doctor,
                        location=location,
                        weekday=weekday,
                        start_time=time(14, 0),
                        end_time=time(18, 0),
                        defaults={
                            'slot_every_min': 20,
                            'max_overbooking': 0
                        }
                    )
                    if tpl2_created:
                        print(f"    Created afternoon schedule for {['Mon','Tue','Wed','Thu','Fri'][weekday]}")
    
    # Create sample patients
    patients_data = [
        {
            'username': 'paciente1',
            'first_name': 'Pedro',
            'last_name': 'Gómez',
            'email': 'pgomez@email.com',
            'phone': '3107778899',
            'document_id': '1012345678',
            'birthdate': date(1990, 5, 15),
            'gender': 'M'
        },
        {
            'username': 'paciente2',
            'first_name': 'Laura',
            'last_name': 'Silva',
            'email': 'lsilva@email.com',
            'phone': '3201112233',
            'document_id': '1023456789',
            'birthdate': date(1985, 8, 22),
            'gender': 'F'
        },
        {
            'username': 'paciente3',
            'first_name': 'Miguel',
            'last_name': 'Torres',
            'email': 'mtorres@email.com',
            'phone': '3154445566',
            'document_id': '1034567890',
            'birthdate': date(2010, 3, 10),
            'gender': 'M'
        }
    ]
    
    for pat_data in patients_data:
        user, created = User.objects.get_or_create(
            username=pat_data['username'],
            defaults={
                'email': pat_data['email'],
                'first_name': pat_data['first_name'],
                'last_name': pat_data['last_name'],
                'role': 'PACIENTE',
                'phone': pat_data['phone'],
                'document_id': pat_data['document_id']
            }
        )
        if created:
            user.set_password('paciente123')
            user.save()
            
            # Create patient profile
            patient, pat_created = Patient.objects.get_or_create(
                user=user,
                defaults={
                    'birthdate': pat_data['birthdate'],
                    'gender': pat_data['gender'],
                    'insurance': 'EPS Salud Total',
                    'consent_given_at': timezone.now()
                }
            )
            if pat_created:
                print(f"  Created patient: {user.get_full_name()}")
    
    # Create holidays
    holidays = [
        {'date': date(2025, 1, 1), 'name': 'Año Nuevo'},
        {'date': date(2025, 1, 6), 'name': 'Día de Reyes'},
        {'date': date(2025, 3, 24), 'name': 'San José'},
        {'date': date(2025, 5, 1), 'name': 'Día del Trabajo'},
        {'date': date(2025, 7, 20), 'name': 'Día de la Independencia'},
        {'date': date(2025, 8, 7), 'name': 'Batalla de Boyacá'},
        {'date': date(2025, 12, 25), 'name': 'Navidad'},
    ]
    
    for holiday_data in holidays:
        holiday, created = Holiday.objects.get_or_create(
            date=holiday_data['date'],
            defaults={'name': holiday_data['name']}
        )
        if created:
            print(f"  Created holiday: {holiday.name}")
    
    print("\nSeed data created successfully!")
    print("\nYou can now login with:")
    print("  Admin: admin / admin123")
    print("  Reception: recepcion1 / recep123")
    print("  Doctors: dr_rodriguez, dra_martinez, dr_lopez / doctor123")
    print("  Patients: paciente1, paciente2, paciente3 / paciente123")

if __name__ == '__main__':
    create_seed_data()