from django.urls import path
from . import views

urlpatterns = [
    path('', views.doctor_list, name='doctor_list'),
    path('<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('schedule/', views.doctor_schedule, name='doctor_schedule'),
    path('patients/', views.doctor_patients, name='doctor_patients'),
    path('availability/', views.doctor_availability, name='doctor_availability'),
    path('availability/day-slots/', views.get_day_slots, name='get_day_slots'),
    path('availability/toggle-slot/', views.toggle_slot_availability, name='toggle_slot_availability'),
    path('availability/add-timeoff/', views.add_timeoff, name='add_timeoff'),
    path('availability/remove-timeoff/', views.remove_timeoff, name='remove_timeoff'),
]
