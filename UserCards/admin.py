from .models import UserProfile
from django.contrib.auth.models import Group
from django.contrib import admin
# Need to import this since auth models get registered on import.
import django.contrib.auth.admin
import django.contrib.auth.models
from django.contrib import auth


class AdminProfile(admin.ModelAdmin):
    list_display = ['user', 'status', 'phone_number', 'address', 'privileges']

#admin.site.unregister(Group)

admin.site.register(UserProfile, AdminProfile)
