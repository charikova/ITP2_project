from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import UserProfile, USER_PROFILE_DATA


USER_STATUSES = [
    ["student", "student"],
    ["instructor", "instructor"],
    ["TA", "TA"],
    ["professor", "professor"],
    ["visiting professor", "visiting professor"]
]

ALL_USER_STATUSES = USER_STATUSES[:]
ALL_USER_STATUSES.append(["librarian", "librarian"])


PRIVILEGES = [
    ["no privileges", "no privileges"],
]

LIBRARIAN_PRIVILEGES = [
    ["no privileges", "no privileges"],
    ["priv1", "priv1"],
    ["priv2", "priv2"],
    ["priv3", "priv3"]
]


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=False)
    address = forms.CharField(required=False)
    phone_number = forms.IntegerField(required=True)
    status = forms.ChoiceField(choices=USER_STATUSES, required=True)
    privileges = forms.ChoiceField(choices=PRIVILEGES, required=True)

    class Meta:
        fields = [
            'username', 'first_name', 'last_name', 'email',  *USER_PROFILE_DATA
        ]
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        address = self.cleaned_data['address']
        phone_number = self.cleaned_data['phone_number']
        status = self.cleaned_data['status']
        privileges = self.cleaned_data['privileges']
        if status == "librarian":
            user.is_staff = True
        if commit:
            user.save(True)
            UserProfile.objects.create(user=user, address=address, phone_number=phone_number, status=status,
                                       privileges=privileges)
            if status == "librarian":
                user.is_staff = True
                lib_group = Group.objects.get(name='Librarian')
                lib_group.user_set.add(user)
                lib_group.save()


class AdminCreateUserForm(CreateUserForm):
    privileges = forms.ChoiceField(choices=LIBRARIAN_PRIVILEGES, required=True)
    status = forms.ChoiceField(choices=ALL_USER_STATUSES, required=True)


class EditPatronForm(UserChangeForm):
    address = forms.CharField(required=False)
    phone_number = forms.IntegerField(required=False)
    status = forms.ChoiceField(choices=USER_STATUSES, required=True)
    privileges = forms.ChoiceField(choices=PRIVILEGES, required=True)

    class Meta(CreateUserForm.Meta):
        fields = [
            'username', 'first_name', 'last_name', 'email', 'password', * USER_PROFILE_DATA
        ]


class AdminEditPatronForm(EditPatronForm):
    status = forms.ChoiceField(choices=ALL_USER_STATUSES, required=True)
    privileges = forms.ChoiceField(choices=LIBRARIAN_PRIVILEGES, required=True)

