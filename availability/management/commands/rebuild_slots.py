from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta, time
import pytz
from availability.models import ScheduleTemplate, TimeOff, Holiday, Slot
from appointments.models import AppointmentType


class Command(BaseCommand):
    help = 'Rebuild appointment slots based on schedule templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--weeks',
            type=int,
            default=12,
            help='Number of weeks to generate slots for (default: 12)'
        )
        parser.add_argument(
            '--from',
            type=str,
            dest='from_date',
            default='today',
            help='Start date (YYYY-MM-DD or "today")'
        )
        parser.add_argument(
            '--doctor',
            type=int,
            help='Generate slots for specific doctor ID only'
        )

    def handle(self, *args, **options):
        weeks = options['weeks']
        from_date_str = options['from_date']
        doctor_id = options.get('doctor')
        
        # Parse start date
        if from_date_str == 'today':
            start_date = timezone.now().date()
        else:
            start_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        
        end_date = start_date + timedelta(weeks=weeks)
        
        self.stdout.write(f'Generating slots from {start_date} to {end_date}')
        
        # Get schedule templates
        templates = ScheduleTemplate.objects.all()
        if doctor_id:
            templates = templates.filter(doctor_id=doctor_id)
        
        if not templates.exists():
            self.stdout.write(self.style.WARNING('No schedule templates found'))
            return
        
        created_count = 0
        blocked_count = 0
        
        for template in templates:
            self.stdout.write(f'Processing template for {template.doctor}')
            
            # Get timezone for location
            tz = pytz.timezone(template.location.timezone)
            
            # Iterate through dates
            current_date = start_date
            while current_date <= end_date:
                # Check if current date matches template weekday
                if current_date.weekday() == template.weekday:
                    # Check for holidays
                    holiday_exists = Holiday.objects.filter(
                        date=current_date
                    ).filter(
                        models.Q(location=template.location) | models.Q(location__isnull=True)
                    ).exists()
                    
                    if holiday_exists:
                        self.stdout.write(f'  Skipping {current_date} (holiday)')
                        current_date += timedelta(days=1)
                        continue
                    
                    # Generate slots for this day
                    start_datetime = tz.localize(datetime.combine(current_date, template.start_time))
                    end_datetime = tz.localize(datetime.combine(current_date, template.end_time))
                    
                    # Check for time offs
                    time_off_exists = TimeOff.objects.filter(
                        doctor=template.doctor,
                        start_dt__lte=end_datetime,
                        end_dt__gte=start_datetime
                    ).exists()
                    
                    # Generate slots
                    slot_duration = timedelta(minutes=template.slot_every_min)
                    current_slot_start = start_datetime
                    
                    while current_slot_start < end_datetime:
                        current_slot_end = current_slot_start + slot_duration
                        
                        # Check if slot already exists
                        existing_slot = Slot.objects.filter(
                            doctor=template.doctor,
                            start_dt=current_slot_start
                        ).first()
                        
                        if not existing_slot:
                            # Determine status
                            if time_off_exists:
                                status = 'BLOQUEADO'
                                blocked_count += 1
                            else:
                                status = 'LIBRE'
                                created_count += 1
                            
                            # Create slot
                            Slot.objects.create(
                                doctor=template.doctor,
                                location=template.location,
                                start_dt=current_slot_start,
                                end_dt=current_slot_end,
                                status=status,
                                source='TPL'
                            )
                        
                        current_slot_start = current_slot_end
                
                current_date += timedelta(days=1)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} free slots and {blocked_count} blocked slots'
            )
        )