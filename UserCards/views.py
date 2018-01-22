from django.shortcuts import render, redirect
from django.http import HttpResponse
from UserCards import models as user_modules
import Documents
from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import SignupForm
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
        # username = form.cleaned_data['username']
        # password = form.cleaned_data['password']
        # user.set_password(password)
        # user.save()
        #
        # user = authenticate(username=username, password=password)
        # if user is not None:
        #     if user.is_active:
        #         login(request, user)
        #         return redirect('Documents:index')
        #
        # return render(request, self.template_name, {'form': form})

