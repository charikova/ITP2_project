from django.shortcuts import redirect, render
from Documents.models import *


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
    type = request.GET['type']
    model = None
    for cls in Document.__subclasses__():
        if cls.type == type:
            model = cls

    if request.method == "GET":
        fields = list(map(lambda x: x.replace(' ', '').replace(')', ''), model.__dict__['__doc__'].split(',')))[1:]
        fields.remove('document_ptr')
        return render(request, "Documents/create_doc.html", {'fields': fields, 'model': model.type})

    elif request.method == "POST":
        new_doc = model()
        for field, value in request.POST.items():
            print(field, value)
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
        for field in fields:
            exec('doc.{0} = request.POST["{0}"]'.format(field[0]))
        doc.save()
        return redirect('../')

