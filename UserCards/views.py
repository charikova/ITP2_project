from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from UserCards import models as user_modules


def index():
    return HttpResponse("hell")


def signup(request):
    return render(request, 'UserCards/signup.html', {})


def make_user(request):
    print('hello world')
    username = request.POST.get("Name")
    surname = request.POST.get("Surname")
    email = request.POST.get("Email")
    password = request.POST.get("Password")
    phone = request.POST.get("Phone")
    user = user_modules.UserCard(name=username, status="student", email=email, password=password, phone_number=phone, surname=surname)
    user.save()
    response = render(request, 'UserCards/index.html', {})
    response.set_cookie(key="password", value=username + str(password) + "id" + str(user.id))
    return response

