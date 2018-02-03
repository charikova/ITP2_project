from django.contrib import admin
from .models import UserProfile


class AdminProfile(admin.ModelAdmin):
    list_display = ['user', 'status', 'phone_number', 'address']


admin.site.register(UserProfile, AdminProfile)