from django.db import models
from django.contrib.auth.models import User

USER_PROFILE_DATA = [
    'phone_number',
    'address',
    'status',
    'photo'
]

class UserProfile(models.Model):
    """
    Extra data for user. (Adding new filed here make sure that you added its
    name to USER_PROFILE_DATA)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    photo = models.ImageField(default="https://lh3.googleusercontent.com/zqfUbCXdb1oGmsNEzNxTjQU5ZlS3x46nQoB83sFbRSlMnpDTZgdVCe_LvCx-rl7sOA=w300")
    status = models.CharField(max_length=250, default='student')

