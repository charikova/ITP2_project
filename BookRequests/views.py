from django.shortcuts import redirect
from django.http import Http404, HttpResponse
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

    if len(request.user.request_set.filter(doc=doc)):
        return HttpResponse('Sorry, but You already have request for this document')
    elif len(request.user.documentcopy_set.filter(doc=doc)):
        return HttpResponse('Sorry, but You already have this document')
    elif doc.is_reference:
        return HttpResponse('Sorry, but this document is reference')
    else:
        doc_request = Request(doc=documents_models.Document.objects.get(id=doc_id),
                      checked_up_by_whom=request.user, timestamp=datetime.datetime.now())
        doc_request.save()
        return HttpResponse('Successfully created new request')


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
    copy = None
    try:
        copy = user.documentcopy_set.get(id=request.GET.get('copy_id'))
    except:
        return HttpResponse('forbidden')
    is_there_requests = len(copy.doc.request_set.all())
    returning_date = user.documentcopy_set.get(doc=copy.doc).returning_date
    returning_date = datetime.datetime(year=returning_date.year,
                                       month=returning_date.month,
                                       day=returning_date.day,
                                       hour=returning_date.hour)
    time_left = returning_date - datetime.datetime.today()
    if copy.renewed:
        return HttpResponse('Sorry, but you already have renewed this document', status=204)
    elif is_there_requests:
        return HttpResponse('Sorry, but this document has outstanding requests', status=204)
    elif time_left.days > 1:
        return HttpResponse('Sorry, but You will have access to renew this document only in {} days'.format(
            time_left.days - 1
        ), status=204)
    else:
        copy.returning_date = datetime.datetime.today() + datetime.timedelta(days=8)
        copy.renewed = True
        copy.save()
        return HttpResponse('You successfully renewed {} for 1 (one) week'.format(copy.doc.title))
