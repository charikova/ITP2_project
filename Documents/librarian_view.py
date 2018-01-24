from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.shortcuts import redirect
from Documents.models import Document


def need_to_be_staff(func):

    def inner(self, request, *args, **kwargs):
        print(request.user.get_group_permissions())
        if request.user.is_staff:
            return func(self, request, *args, **kwargs)
        return redirect('/')

    return inner



class ModifyDocument:
    model = Document
    template_name = 'Documents/modify_doc.html'
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
    pass


class CreateDocument(ModifyDocument, CreateView):
    pass