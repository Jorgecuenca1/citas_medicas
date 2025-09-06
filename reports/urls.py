from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('appointments/', views.appointments_report, name='appointments_report'),
    path('occupancy/', views.occupancy_report, name='occupancy_report'),
    path('cancellations/', views.cancellations_report, name='cancellations_report'),
]
