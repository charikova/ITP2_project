from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.shortcuts import redirect, render
from Documents.models import *


def need_to_be_staff(func):
    """
    the decorator that wrap "get" method to limit non-staff users
    """
    def inner(request, *args, **kwargs):
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        return redirect('/')

    return inner

def need_logged_in(func):

    def inner(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return redirect('/')

    return inner



class ModifyDocument:
    '''
    Base class for librarian's possibilities: delete/create/update etc.
    '''
    model = Document
    template_name = 'Documents/modify_doc.html' # base template which includes
        # expression {{ form.as_p }} for default html paragraph
    success_url = '/'
    fields = [
        'cover', 'title', 'authors', 'price', 'copies', 'keywords'
    ]

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('/')


class DeleteDocument(ModifyDocument, DeleteView):
    template_name = 'Documents/del_doc.html'


def get_fields_of(doc, excess_fields=['document_ptr_id', '_state', 'id']):
    fields = dict()
    for key, value in doc.__dict__.items():
        if key not in excess_fields:
            fields[key] = value
    fields = list(
        map(lambda key: (key, str(fields[key])), fields))
    return fields


def get_doc(request, pk):
    doc = None
    for Type in Document.__subclasses__():
        if Type.objects.filter(pk=pk):
            doc = Type.objects.get(pk=pk)
    return doc


class CreateDocument(ModifyDocument, CreateView):

    def get(self, request, *args, **kwargs):
        self.fields = list(map(lambda x: x.replace(' ', '').replace(')', ''), self.model.__dict__['__doc__'].split(',')))[1:]
        self.fields.remove('type')
        self.extra_context = {'model': self.model.type}
        return super(CreateDocument, self).get(request, *args, **kwargs)

# def create_doc(request):
#     if request.method == "GET":
#         type = request.GET['type']
#         model = None
#         for cls in Document.__subclasses__():
#             if cls.type == type:
#                 model = cls
#         fields = list(map(lambda x: x.replace(' ', '').replace(')', ''), model.__dict__['__doc__'].split(',')))[1:]
#         fields.remove('type')
#         return render(request, "Documents/create_doc.html", {'fields': fields, 'model': model.type})
#     elif request.method == "POST":
#         pass


@need_to_be_staff
def add_doc(request):
    return render(request, 'Documents/add_doc.html', {'clss': list(map(lambda x: x.type, Document.__subclasses__()))[:-1]})


@need_to_be_staff
def update_doc(request, pk):
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