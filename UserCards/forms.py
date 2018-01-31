from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


USER_STATUSES = [
    [1, "student"],
    [2, "faculty"],
    [3, "librarian"],
]


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    address = forms.CharField(required=True)
    phone_number = forms.IntegerField(required=True)
    status = forms.ChoiceField(choices=USER_STATUSES, required=True)

    class Meta:
        fields = [
            'username', 'first_name', 'last_name', 'email', 'address', 'phone_number', 'status'
        ]
        model = User


    def save(self, commit=True):
        user = super(CreateUserForm, self).save(commit=False)
        user.address = self.cleaned_data['address']
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save(True)


class EditPatronForm(UserChangeForm):
    address = forms.CharField(required=True)
    phone_number = forms.IntegerField(required=True)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'address'
        ]

