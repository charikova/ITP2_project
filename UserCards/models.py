from django.db import models

class UserCard(models.Model):
    name = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=250)
    times_up = models.IntegerField()


class FacultyCard(UserCard):
    times_up = 4


class StudentCard(UserCard):
    times_up = 3

