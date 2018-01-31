from django.db import models
from django.contrib.auth.models import AbstractBaseUser, User

class UserCard(models.Model):
    name = models.CharField(default='', max_length=250)
    surname = models.CharField(max_length=250, default='')
    status = models.CharField(max_length=7)
    address = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=250)
    email = models.EmailField(default='')
    password = models.CharField(default='123456', max_length=250)
    session_id = models.CharField(default='', max_length=500)


class FacultyCard(UserCard):
    status = 'faculty'


class StudentCard(UserCard):
    status = 'student'


class CustomUser(AbstractBaseUser):

    email = models.EmailField(max_length=250, unique=True)
    name = models.CharField(max_length=250)
    surname = models.CharField(max_length=250)
    status = models.CharField(max_length=250)
    staff = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    admin = models.BooleanField(default=False)
    address = models.CharField(max_length=250)
    phone_number = models.IntegerField()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['email', 'password', 'name', 'surname', 'address', 'phone_number']


class MyUser(User):
    address = models.CharField(max_length=250, default='Universitetskya 1')
    phone_number = models.IntegerField(default=11111)
    status = models.CharField(max_length=250, default='student')

    REQUIRED_FIELDS = ['email', 'password', 'name', 'surname', 'address', 'phone_number']


class UserCardProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=250, default='Universitetskya 1')
    phone_number = models.IntegerField(default=11111)
    status = models.CharField(max_length=250, default='student')
