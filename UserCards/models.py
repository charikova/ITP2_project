from django.db import models

class UserCard(models.Model):
    name = models.CharField(max_length=250)
    status = models.CharField(max_length=7)
    address = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=250)
    times_up = models.IntegerField()


class FacultyCard(UserCard):
    status = 'faculty'
    times_up = 4


class StudentCard(UserCard):
    status = 'student'
    times_up = 3

