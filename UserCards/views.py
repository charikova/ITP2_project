from django.shortcuts import render, redirect
from django.http import HttpResponse
from UserCards import models as user_modules
import Documents
from django.contrib.auth import authenticate, login
from django.views.generic import View, DetailView
from .forms import SignupForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



class SignupView(View):

    template_name = "UserCards/signup.html"

    def get(self, request):
        form = SignupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
        return redirect('/user/signup/')


def user_card_info(request):
    context = {'user': request.user}
    return render(request, 'UserCards/index.html', context)

