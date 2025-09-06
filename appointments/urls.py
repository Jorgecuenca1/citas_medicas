from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('search/', views.appointment_search, name='appointment_search'),
    path('book/<int:slot_id>/', views.appointment_book, name='appointment_book'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/confirm/', views.appointment_confirm, name='appointment_confirm'),
    path('<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('<int:pk>/checkin/', views.appointment_checkin, name='appointment_checkin'),
    path('<int:pk>/attend/', views.appointment_attend, name='appointment_attend'),
    path('<int:pk>/reschedule/', views.appointment_reschedule, name='appointment_reschedule'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('my-appointments/', views.patient_appointments, name='patient_appointments'),
    path('api/doctors-by-specialty/', views.get_doctors_by_specialty, name='doctors_by_specialty'),
]
