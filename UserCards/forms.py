from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    address = forms.CharField(required=True)
    phone_number = forms.CharField(required=True)

    class Meta:
        fields = [
            'email', 'username', 'password', 'address', 'phone_number'
        ]
        model = User


    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.address = self.cleaned_data['address']
        user.phone_number = self.cleaned_data['phone_number']
        user.status = self.cleaned_data['status']

        if commit:
            user.save(True)


