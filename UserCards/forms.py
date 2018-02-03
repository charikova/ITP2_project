from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import UserProfile, USER_PROFILE_DATA


USER_STATUSES = [
    [1, "student"],
    [2, "faculty"],
    [3, "librarian"],
]

EDIT_PROFILE_DATA = USER_PROFILE_DATA
EDIT_PROFILE_DATA.remove('status')


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    address = forms.CharField(required=True)
    phone_number = forms.IntegerField(required=True)
    status = forms.ChoiceField(choices=USER_STATUSES, required=True)

    class Meta:
        fields = [
            'username', 'first_name', 'last_name', 'email', *USER_PROFILE_DATA
        ]
        model = User


    def save(self, commit=True):
        user = super(CreateUserForm, self).save(commit=False)
        address = self.cleaned_data['address']
        phone_number = self.cleaned_data['phone_number']
        status = dict(USER_STATUSES)[int(self.cleaned_data['status'])]
        if status == "librarian":
            user.is_staff = True
        if commit:
            user.save(True)
            UserProfile.objects.create(user=user, address=address, phone_number=phone_number, status=status)
            if status == "librarian":
                user.is_staff = True
                lib_group = Group.objects.get(name='Librarian')
                lib_group.user_set.add(user)


class EditPatronForm(UserChangeForm):
    address = forms.CharField(required=True)
    phone_number = forms.IntegerField(required=True)

    class Meta(CreateUserForm.Meta):
        fields = [
            'username', 'first_name', 'last_name', 'email', *EDIT_PROFILE_DATA
        ]

