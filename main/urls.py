from django.urls import path
from .views import *


urlpatterns = [
    path('delete-readings/', delete_readings, name='delete-readings'),
    path('delete-all-readings/', delete_all_readings, name='delete_all_readings'),
]
