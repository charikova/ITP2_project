from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, Http404
import datetime
from Documents.librarian_view import *


class IndexView(ListView):
    template_name = 'Documents/index.html'
    model = Document
    context_object_name = 'documents'
    paginate_by = 10


def document_detail(request, pk):
    print(request.user)
    doc = None
    for Type in Document.__subclasses__():
        if Type.objects.filter(pk=pk):
            doc = Type.objects.get(pk=pk)
    context = {'user_has_doc':len(request.user.documentcopy_set.all().filter(
                                    doc=Document.objects.get(id=int(request.path.replace('/', '')))))}
    context['doc'] = doc
    context['cover'] = doc.__dict__['cover']
    context['fields'] = dict()
    excess_fields = ['document_ptr_id', '_state', 'id', 'cover', 'keywords', 'room', 'level']
    for key, value in doc.__dict__.items():
        if key not in excess_fields:
            context['fields'][key] = value
    context['fields'] = list(map(lambda key: (key.replace('_', ' '), context['fields'][key]), context['fields']))
    return render(request, 'Documents/doc_inf.html', context)


@need_logged_in
def checkout(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    user = request.user
    if user.is_staff:
        raise Http404('staff can not take documents')
    if user.documentcopy_set.filter(doc=doc):
        return redirect('/{0}/'.format(pk))
    if doc.copies >= 0:
        new_request = BookRequest(doc=doc, checked_up_by_whom=user, )
        new_request.save()
    return redirect('/{0}/'.format(pk))
