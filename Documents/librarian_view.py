from django.shortcuts import redirect, render
from Documents.models import *
from BookRequests.models import Request
from django.views.generic import ListView
from UserCards.forms import USER_STATUSES
from django.core.mail import send_mail
import Documents.models as documents_models
from innopolka import settings

def required_staff(func):
    """
    limitation for non-staff users
    """
    def inner(request, *args, **kwargs):
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        return redirect('/')

    return inner


def need_logged_in(func):
    """
    limitation for anonymous users
    """
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return redirect('/')

    return inner
    

@required_staff
def del_doc(request, pk):
    """
    delete document
    :param pk: id of document to delete
    """
    doc = Document.objects.get(pk=pk)
    doc.delete()
    return redirect('/')


def get_fields_of(doc, excess_fields=['document_ptr_id', '_state', 'id']):
    """
    :param doc: document to find all fields of class
    :param excess_fields: fields which needed not to be included
    :return: fields of document
    """
    fields = dict()
    for key, value in doc.__dict__.items():
        if key not in excess_fields:
            fields[key] = value
    fields = list(
        map(lambda key: (key, str(fields[key])), fields))
    return fields


def get_doc(request, pk):
    """
    :param request: url request
    :param pk: id of document in db
    :return: document that has this pk. Document will be a subclass of Document.
    """
    doc = None
    for Type in Document.__subclasses__():
        if Type.objects.filter(pk=pk):
            doc = Type.objects.get(pk=pk)
    return doc


@required_staff
def create_doc(request):
    """
    creating document object (in real subclass of Document object) and saving in db
    :param request: url request
    """
    type_ = request.GET['type']
    model = None
    for cls in Document.__subclasses__():
        if cls.type == type_:
            model = cls

    if request.method == "GET":
        fields = list(map(lambda x: x.replace(' ', '').replace(')', ''), model.__dict__['__doc__'].split(',')))[1:]
        fields.remove('document_ptr')
        return render(request, "Documents/create_doc.html", {'fields': fields, 'model': model.type})

    elif request.method == "POST":
        new_doc = model()
        for field, value in request.POST.items():
            if type(value) == str:  # hack protection
                value = value.replace('#', '').replace('(', '').replace(')', '').replace(';', '')
            exec('new_doc.{0} = "{1}"'.format(field, value))
        new_doc.save()
        return redirect('/{}/'.format(new_doc.id))


@required_staff
def add_doc(request):
    """
    :return: html page with the list of all subclasses of Document model
    """
    return render(request, 'Documents/add_doc.html',
                  {'clss': list(map(lambda x: x.type, Document.__subclasses__()))})


@required_staff
def update_doc(request, pk):
    """
    update some fields of document
    :param pk: id of document needed to update
    """
    doc = get_doc(request, pk)
    fields = get_fields_of(doc)

    if request.method == "GET":
        return render(request, 'Documents/update_doc.html',
                      {'doc': doc, 'cover': doc.__dict__['cover'], 'fields': fields})
    elif request.method == "POST":

        n_of_copies = 0
        if int(request.POST['copies']) > doc.copies:
            n_of_copies = int(request.POST['copies']) - doc.copies

        for field in fields:
            exec('doc.{0} = request.POST["{0}"]'.format(field[0]))
        doc.save()

        if 'need_to_notify' in request.POST:

            queue = RequestsView().get_queryset()

            for query in queue:
                if str(query['doc']).split(';')[0] == str(request.POST['title'].split(';')[0]):
                    message = "Hello! Now " + str(doc.title) + " available. You can " \
                                                               "take your " + str(doc.type) + "."

                    if n_of_copies >= len(query['users']):
                        for user in query['users']:
                            to = user.email
                            send_mail('Document available', message, settings.EMAIL_HOST_USER, [to])
                    else:
                        for i in range(0, n_of_copies):
                            to = query['users'][i].email
                            send_mail('Document available', message, settings.EMAIL_HOST_USER, [to])
                    break

        return redirect('../')


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

    def get_queryset(self):
        status_priorities = [status[0] for status in USER_STATUSES]
        qs = super().get_queryset().order_by('-timestamp')
        result = list()
        for req in qs:  # sort users by status priorities and time request was made
            req_item = {'doc': req.doc, 'timestamp': req.timestamp, 'id': req.id}
            users = [(status_priorities.index(u.userprofile.status), u) for u in list(req.users.all())]
            if len(users) != 1:  # sort users according to status priorities
                users.sort(key=lambda x: -x[0])
            req_item['users'] = [u[1] for u in users]
            result.append(req_item)
        return result

