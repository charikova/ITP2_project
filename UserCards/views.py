from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.views.generic import View, ListView
import Documents.models as documents_models
from Documents.librarian_view import need_logged_in
from .forms import *
import datetime


class UserList(ListView):
    template_name = 'UserCards/user_list.html'
    model = User

class CreateUserView(View):
    """
    User creation view
    """
    template_name = "UserCards/signup.html"

    def get(self, request):
        if request.user.is_staff:
            form = CreateUserForm()
            return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_staff:
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                user = authenticate(username=username, password=password)
                user.save()
                return redirect("/")
            return redirect('/user/create_user/')



class EditCardView(View):

    def post(self, request):
        form = EditPatronForm(request.POST, instance=request.user)
        print(form)
        if form.is_valid():
            form.save()
            return redirect('/user/')

    def get(self, request):
        form = EditPatronForm(instance=request.user)
        return render(request, 'UserCards/edit.html', {'form': form})


@need_logged_in
def user_card_info(request):
    """
    shows users their information and docs they currently checking out with time left to return them back
    """
    user = request.user
    if request.GET.get('id') is not None:
        if request.user.is_staff:
            user = User.objects.get(id=request.GET.get('id'))
        else:
            return redirect('/')

    for profile_field in USER_PROFILE_DATA: # take all data from user's profile and put into user object
        exec('user.{0} = user.userprofile.{0}'.format(profile_field))

    fields = list()
    for field in CreateUserForm.Meta.fields: # take all fields from "user creation form" which should be displayed
        fields.append((field.replace('_', ' ').capitalize(), eval('user.{}'.format(field))))

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
            document_copy.time_left = "Time to return: " + str(int(temp / 3600)) + "h:" + str(int(temp % 3600 / 60))+"m"
        elif 3600 > temp >= 60:
            document_copy.time_left = "Time to return: " + str(int(temp / 60))
        elif 60 > temp > 0:
            document_copy.time_left = "Time to return: " + str(int(temp))
        else:
            day = (datetime.datetime.now(UTC())-document_copy.returning_date).days

            print(day)
            if 100*int(day) <= document_copy.doc.price:
                document_copy.fine_price = 100*int(day)
            else:
                document_copy.fine_price = document_copy.doc.price

            document_copy.time_left = 'You need to pay: ' + str(document_copy.fine_price)

        document_copy.save()

    context = {'fields': fields, 'copies': user.documentcopy_set.all()}
    return render(request, 'UserCards/index.html', context)


@need_logged_in
def return_copies(request):
    """
    returns copies back. Increases size of copies of document.
    """
    chosen_copies = [documents_models.DocumentCopy.objects.get(id=int(id)) for id in request.POST.keys() if
                     id.isdigit()] # get copies user chose via checkboxes
    for copy in chosen_copies:
        copy.doc.copies += 1
        copy.doc.save()
        copy.delete()
    return redirect('/user/')
