from django.db import models
from django.contrib.auth.models import User

USER_PROFILE_DATA = [
    'phone_number',
    'address',
    'status'
]

class UserProfile(models.Model):
    """
    Extra data for user. (Adding new filed here make sure that you added its
    name to USER_PROFILE_DATA)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    status = models.CharField(max_length=250, default='student')

