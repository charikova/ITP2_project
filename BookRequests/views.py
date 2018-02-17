from django.shortcuts import redirect
from django.http import Http404
from Documents.librarian_view import required_staff, need_logged_in
from django.contrib.auth.models import User
from django.views.generic import ListView
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
        if request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('/')


@need_logged_in
def make_new(request):
    """
    creates new request from user
    """
    doc_id = request.GET.get('doc')
    try:
        doc = documents_models.Document.objects.get(id=doc_id)
    except:
        raise Http404('You cannot request this document')

    user_can_request = not len(request.user.request_set.filter(doc=doc)) and \
                       not len(request.user.documentcopy_set.filter(doc=doc))
    if user_can_request:
        if doc.copies > 0 and not doc.is_reference:
            doc_request = Request(doc=documents_models.Document.objects.get(id=doc_id),
                          checked_up_by_whom=request.user, timestamp=datetime.datetime.now())
            doc_request.save()
    return redirect('/' + str(doc_id))


@required_staff
def approve_request(request):
    """
    gives book to particular user
    """
    try:
        user = User.objects.get(pk=request.GET.get('user_id'))
        doc_request = Request.objects.get(pk=request.GET.get('req_id'))
    except:
        return Http404
    doc = doc_request.doc
    if not doc.is_reference and doc.copies > 0:
        doc.copies -= 1
        doc.save()
        days = 21  # for student
        if doc.type == "AVFile" or doc.type == "JournalArticle":
            days = 14
        elif user.userprofile.status == 'faculty':
            days = 28
        elif doc.is_bestseller:
            days = 14
        copy = documents_models.DocumentCopy(doc=doc,
                                checked_up_by_whom=user, returning_date=(
                datetime.date.today() + datetime.timedelta(days=days)).strftime("%Y-%m-%d"))
        copy.save()
    doc_request.delete()
    return redirect('/requests')


@need_logged_in
def refuse(request):
    """
    refuses request made by user
    """
    doc_request = Request.objects.get(id=request.GET.get('req_id'))
    doc_request.delete()
    return redirect('/requests/')


@required_staff
def return_doc(request):
    """
    taking document back (user has returned his document)
    """
    copy_instance = documents_models.DocumentCopy.objects.get(pk=request.GET.get('copy_id'))
    user_id = copy_instance.checked_up_by_whom.id
    copy_instance.doc.copies += 1
    copy_instance.doc.save()
    copy_instance.delete()
    return redirect('/user/?user_id=' + str(user_id))


@need_logged_in
def renew(request):
    user = request.user
    copy = user.documentcopy_set.filter(id=request.GET.get('copy_id'))
    if copy:
        copy = copy[0]
        # update date
    return redirect('/' + str(copy.doc.id))
