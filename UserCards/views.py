from django.shortcuts import render, redirect
from django.http import HttpResponse
from UserCards import models as user_modules
import Documents
from django.contrib.auth import authenticate, login
from django.views.generic import View, DetailView
from .forms import *



class SignupView(View):

    template_name = "UserCards/signup.html"

    def get(self, request):
        form = SignupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            login(request, request.user)
            return redirect("/")
        return redirect('/user/signup/')


def user_card_info(request):
    if not request.user.is_anonymous:
        context = {'user': request.user}
        return render(request, 'UserCards/index.html', context)
    else:
        return redirect('/user/login/')


class EditCardView(View):

    def post(self, request):
        form = EditPatronForm(request, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/user/')

    def get(self, request):
        form = EditPatronForm(instance=request.user)
        return render(request, 'UserCards/edit.html', {'form': form})