from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic import View
import Documents.models as documents_models
from django.shortcuts import get_object_or_404, Http404
import UserCards.models as usercard_models
from .forms import *
import datetime


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
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            user.save()
            login(request, user)
            return redirect("/")
        return redirect('/user/signup/')


class EditCardView(View):

    def post(self, request):
        print(request.POST)
        form = EditPatronForm(request.POST, instance=request.user)
        print(form)
        if form.is_valid():
            print('form is alright')
            form.save()
            return redirect('/user/')
        print('wrong form')

    def get(self, request):
        form = EditPatronForm(instance=request.user)
        return render(request, 'UserCards/edit.html', {'form': form})


@need_logged_in
def user_card_info(request):
    user = request.user
    print(dir(user))
    documents_copy = user.documentcopy_set.all()

    ZERO = datetime.timedelta(0)
    class UTC(datetime.tzinfo):
        def utcoffset(self, dt):
            return ZERO

        def tzname(self, dt):
            return "UTC"

        def dst(self, dt):
            return ZERO

    for document_copy in documents_copy:
        temp = (document_copy.returning_date - datetime.datetime.now(UTC())).days*24*3600 + (document_copy.returning_date - datetime.datetime.now(UTC())).seconds
        print(temp)
        if temp >= 3600:
            document_copy.time_left = str(int(temp / 3600)) + "h:" + str(int(temp % 3600 / 60))+"m"
        elif 3600 > temp >= 60:
            document_copy.time_left = str(int(temp / 60))
        else:
            document_copy.time_left = '0'

        document_copy.save()

    context = {'user': user, 'copies': user.documentcopy_set.all()}
    return render(request, 'UserCards/index.html', context)


@need_logged_in
def return_copies(request):
    user = request.user
    chosen_copies = [documents_models.DocumentCopy.objects.get(id=int(id)) for id in request.POST.keys() if
                     id.isdigit()]
    for copy in chosen_copies:
        copy.doc.copies += 1
        copy.doc.save()
        copy.delete()
    context = {'user': user, 'copies': user.documentcopy_set.all()}
    return render(request, 'UserCards/index.html', context)


class BookRequestsView(ListView):
        template_name = 'UserCards/bookrequests.html'
        model = documents_models.BookRequest
        context_object_name = 'requests'
        paginate_by = 10


def givebook(request, pk,  booktaker):

    user = User.objects.get(pk=booktaker)
    br = documents_models.BookRequest.objects.get(pk=pk)
    doc = br.doc
    if doc.copies > 0:
        doc.copies -= 1
        doc.save()
        if True or user.status == 'student':
            new_copy = documents_models.DocumentCopy(doc=doc,
                                    checked_up_by_whom=user, returning_date=(
                        datetime.date.today() + datetime.timedelta(days=14)).strftime("%Y-%m-%d"))
        else:
            new_copy = documents_models.DocumentCopy(doc=doc,
                                    checked_up_by_whom=user, returning_date=(
                        datetime.date.today() + datetime.timedelta(days=21)).strftime("%Y-%m-%d"))

        new_copy.save()
        br.delete()


    return redirect('bookrequests')



