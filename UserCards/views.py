from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views.generic import View
import Documents.models as documents_models
from .forms import *


def need_logged_in(func):

    def inner(request, *args, **kwargs):
        user = request.user
        if not user.is_anonymous:
            return func(request, *args, **kwargs)
        else:
            return redirect('/user/login/')

    return inner


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


class EditCardView(View):

    def post(self, request):
        form = EditPatronForm(request, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/user/')

    def get(self, request):
        form = EditPatronForm(instance=request.user)
        return render(request, 'UserCards/edit.html', {'form': form})


@need_logged_in
def user_card_info(request):
    user = request.user
    print(dir(user))
    context = {'user': user, 'copies': user.documentcopy_set.all()}
    return render(request, 'UserCards/index.html', context)


@need_logged_in
def return_copies(request):
    user = request.user
    chosen_copies = [documents_models.DocumentCopy.objects.get(id=int(id)) for id in request.POST.keys() if id.isdigit()]
    for copy in chosen_copies:
        copy.doc.copies += 1
        copy.doc.save()
        copy.delete()
    context = {'user': user, 'copies': user.documentcopy_set.all()}
    return render(request, 'UserCards/index.html', context)
