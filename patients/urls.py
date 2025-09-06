from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('create/', views.patient_create, name='patient_create'),
    path('profile/create/', views.patient_profile_create, name='patient_profile_create'),
    path('<int:pk>/', views.patient_detail, name='patient_detail'),
    path('<int:pk>/update/', views.patient_update, name='patient_update'),
]
