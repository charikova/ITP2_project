from django.db import models
from django.contrib.auth.models import User

USER_PROFILE_DATA = [
    'status',
    'phone_number',
    'address',
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    status = models.CharField(max_length=250, default='student')


