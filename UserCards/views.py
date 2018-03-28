from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.http import Http404
from django.db.models import Q
from django.views.generic import View, ListView
from Documents.librarian_view import need_logged_in, required_staff
from .forms import *
import datetime


class CreateUserView(View):
    """
    user creation view
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
                return redirect("/user/all/?p=on&l=on")
            return redirect('/user/create_user/')


class EditCardView(View):

    def post(self, request, id):
        user = User.objects.get(id=id)
        form = EditPatronForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            for field in USER_PROFILE_DATA:
                exec('user.userprofile.{0} = form.cleaned_data["{0}"]'.format(field))
            if user.userprofile.status == 'librarian':
                user.is_staff = True
            else:
                user.is_staff = False
            user.userprofile.save()
            user.save()
            if user.userprofile.status == "librarian":
                lib_group = Group.objects.get(name='Librarian')
                lib_group.user_set.add(user)
                lib_group.save()
            return redirect('/user/?id='+str(id))

    def get(self, request, id):
        init_fields = {'address': User.objects.get(id=id).userprofile.address,
                       'status': User.objects.get(id=id).userprofile.status,
                       'phone_number': User.objects.get(id=id).userprofile.phone_number,
                       'password': User.objects.get(id=id).password
                       }
        form = EditPatronForm(instance=User.objects.get(id=id), initial=init_fields)
        return render(request, 'UserCards/edit.html', {'form': form})


@required_staff
def delete_user(request, id):
    User.objects.get(id=id).delete()
    return redirect('/user/all/?p=on&l=on')


@need_logged_in
def user_card_info(request):
    """
    shows user's information and docs they currently are checking out with time left to return them back
    """
    user = request.user
    context = dict()
    if request.GET.get('id') is None:
        return Http404('No such user in library')
    # only librarians are allowed to see user profile by id
    if (user.is_staff and user.id != int(request.GET.get('id'))) or \
            (user.is_authenticated and user.id == int(request.GET.get('id'))):
        user = User.objects.get(id=request.GET.get('id'))
        context['current_user'] = user
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
        temp = (document_copy.returning_date - datetime.datetime.now()).days*24*3600 + \
               (document_copy.returning_date - datetime.datetime.now()).seconds

        if temp >= 3600:
            document_copy.time_left = "Time to return: " + str(int(temp / (3600*24))) + "days " + str(int(temp % (3600*24) / 3600)) + "h:" + str(int(temp % 3600 / 60))+"m"
        elif 3600 > temp >= 60:
            document_copy.time_left = "Time to return: " + str(int(temp / 60)) + "m"
        elif 60 > temp > 0:
            document_copy.time_left = "Time to return: " + str(int(temp)) + "s"
        else:
            day = (datetime.datetime.now()-document_copy.returning_date).days

            if 100*int(day) <= document_copy.doc.price:
                document_copy.fine_price = 100*int(day)
            else:
                document_copy.fine_price = document_copy.doc.price

            document_copy.time_left = 'You need to pay: ' + str(document_copy.fine_price)

        document_copy.save()

    context['fields'] = fields
    context['copies'] = user.documentcopy_set.all()
    return render(request, 'UserCards/index.html', context)


class AllUsersView(ListView):
    model = User
    template_name = 'UserCards/user_list.html'
    context_object_name = 'users'

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().get(self, request, *args, **kwargs)
        else:
            return redirect('/')

    def get_queryset(self):
        query = self.request.GET.get('uq')
        in_patrons = self.request.GET.get('p')
        in_labs = self.request.GET.get('l')
        db_query = Q(is_staff=None)
        if in_patrons:
            db_query |= Q(is_staff=False)
        if in_labs:
            db_query |= Q(is_staff=True)
        if query:
            db_query &= (Q(username__icontains=query) |
                                       Q(first_name__icontains=query) |
                                       Q(last_name__icontains=query))
        return User.objects.filter(db_query).order_by('username')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uq'] = self.request.GET.get('uq')
        context['p'] = self.request.GET.get('p')
        context['l'] = self.request.GET.get('l')
        return context

