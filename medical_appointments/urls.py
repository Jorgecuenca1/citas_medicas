"""
URL configuration for medical_appointments project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import login_view, logout_view, dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # Apps URLs
    path('accounts/', include('accounts.urls')),
    path('appointments/', include('appointments.urls')),
    path('patients/', include('patients.urls')),
    path('doctors/', include('doctors.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)