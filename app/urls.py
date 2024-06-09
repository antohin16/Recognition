"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path
from main import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('delete-readings/', views.delete_readings, name='delete_readings'),
    path('delete-all-readings/', views.delete_all_readings, name='delete_all_readings'),
    path('recognize/', views.recognize, name='recognize'),
    path('readings/', views.readings, name='readings'),
    path('export/readings/pdf/', views.export_readings_pdf, name='export_readings_pdf'),
    path('export/readings/excel/', views.export_readings_excel, name='export_readings_excel'),
    path('save_reading/', views.save_reading, name='save_reading'),
    path('water_upload/', views.water_upload, name='water_upload'),
    path('water_recognize/', views.water_recognize, name='water_recognize'),
    path('register/', views.register, name='register'),
    path('login_required/', views.login_required_view, name='login_required'),
    path('login/', views.login_request, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('edit-reading/<int:reading_id>/', views.edit_reading, name='edit_reading'),
    path('save_edited_reading/', views.save_edited_reading, name='save_edited_reading'),
    path('edit/water_reading/<int:reading_id>/', views.edit_water_reading, name='water_edit_reading'),
    path('save_edited_water_reading/', views.save_edited_water_reading, name='save_edited_water_reading'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

