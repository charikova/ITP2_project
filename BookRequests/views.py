from django.shortcuts import render, redirect
from Documents.librarian_view import required_staff, need_logged_in
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView
import Documents.models as documents_models
from .models import Request
import datetime


class RequestsView(ListView):
    """
    view of all requests made by users
    """
    template_name = 'BookRequests/bookrequests.html'
    model = Request
    context_object_name = 'requests'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('/')


@need_logged_in
def make_new(request):
    """
    creates new request from user
    """
    doc_id = request.GET['doc']
    doc_request = Request(doc=documents_models.Document.objects.get(id=doc_id),
                          checked_up_by_whom=request.user, timestamp=datetime.datetime.now())
    doc_request.save()
    return redirect('/')


@required_staff
def approve_request(request):
    """
    gives book to particular user
    """
    user = User.objects.get(pk=request.GET.get('user_id'))
    doc_request = Request.objects.get(pk=request.GET.get('req_id'))
    doc = doc_request.doc
    if doc.copies > 0:
        doc.copies -= 1
        doc.save()
        if user.userprofile.status == 'student':
            new_copy = documents_models.DocumentCopy(doc=doc,
                                    checked_up_by_whom=user, returning_date=(
                        datetime.date.today() + datetime.timedelta(days=14)).strftime("%Y-%m-%d"))
        else:
            new_copy = documents_models.DocumentCopy(doc=doc,
                                    checked_up_by_whom=user, returning_date=(
                        datetime.date.today() + datetime.timedelta(days=21)).strftime("%Y-%m-%d"))

        new_copy.save()
        doc_request.delete()
    return redirect('/requests')


@required_staff
def refuse(request):
    """
    refuses request made by user
    """
    doc_request = Request.objects.get(id=request.GET.get('req_id'))
    doc_request.delete()
    return redirect('/requests/')


@required_staff
def takebook(request):
    """
    taking document back (user has returned his document)
    """
    copy_instance = documents_models.DocumentCopy.objects.get(pk=request.GET.get('copy_id'))
    copy_instance.doc.copies += 1
    copy_instance.doc.save()
    copy_instance.delete()
    return redirect('/requests/')


@need_logged_in
def renew(request):
    pass