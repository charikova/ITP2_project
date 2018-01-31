from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserCardProfile


class UserAdmin(BaseUserAdmin):
    inlines = [UserCardProfile]


class UserInline(admin.StackedInline):
    model = UserCardProfile
    can_delete = False


admin.site.register(UserCardProfile)


