from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

class Reading(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_url = models.CharField(max_length=255, blank=False)
    reading_value = models.CharField(max_length=30, blank=False)
    date_posted = models.DateTimeField(default=now)
    METER_TYPE_CHOICES = [
        ('factory', 'Заводской'),
        ('water', 'Водяной')
    ]
    meter_type = models.CharField(max_length=10, choices=METER_TYPE_CHOICES, default='factory')

    def __str__(self):
        return f"Reading('{self.image_url}', '{self.reading_value}', '{self.date_posted}')"




