from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.shortcuts import redirect
from Documents.models import Document


def need_to_be_staff(func):
    """
    the decorator that wrap "get" method to limit non-staff users
    """
    def inner(self, request, *args, **kwargs):
        print(request.user.get_group_permissions())
        if request.user.is_staff:
            return func(self, request, *args, **kwargs)
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
        'type', 'cover', 'title', 'authors', 'price', 'copies', 'keywords'
    ]

    @need_to_be_staff
    def get(self, request, *args, **kwargs):
        return super(ModifyDocument, self).get(request, *args, **kwargs)


class DeleteDocument(ModifyDocument, DeleteView):
    pass


class UpdateDocument(ModifyDocument, UpdateView):
    success_url = '../'


class CreateDocument(ModifyDocument, CreateView):
    pass