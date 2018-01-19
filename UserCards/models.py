from django.db import models

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

