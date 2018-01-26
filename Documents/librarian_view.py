from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.shortcuts import redirect
from Documents.models import *


def need_to_be_staff(func):
    """
    the decorator that wrap "get" method to limit non-staff users
    """
    def inner(self, request, *args, **kwargs):
        if request.user.is_staff:
            return func(self, request, *args, **kwargs)
        return redirect('/')

    return inner

def need_logged_in(func):

    def inner(request, *args, **kwargs):
        if not request.user.is_anonymous:
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

    @need_to_be_staff
    def get(self, request, *args, **kwargs):
        return super(ModifyDocument, self).get(request, *args, **kwargs)


class DeleteDocument(ModifyDocument, DeleteView):
    pass


class UpdateDocument(ModifyDocument, UpdateView):
    success_url = '../'


class CreateDocument(CreateView):
    template_name = 'Documents/modify_doc.html'  # base template which includes
    # expression {{ form.as_p }} for default html paragraph
    success_url = '/'
    fields = [
        'cover', 'title', 'authors', 'price', 'copies', 'keywords'
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(kwargs)
        self.model = Book

    @need_to_be_staff
    def get(self, request, *args, **kwargs):
        print(request)
        self.fields += ['publisher', 'edition', 'publication_date']
        return super(CreateDocument, self).get(request, *args, **kwargs)


def create_doc(request):
    type = request.GET['type']
    cd = CreateDocument(type=type)
    return CreateDocument.as_view()