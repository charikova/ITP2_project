
from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, Http404
import datetime
from Documents.librarian_view import *


class IndexView(ListView):

    template_name = 'Documents/index.html'
    model = Document
    context_object_name = 'documents'
    paginate_by = 10


class DocumentDetail(DetailView):
    template_name = 'Documents/doc_inf.html'
    model = Document
    context_object_name = 'doc'

    def get(self, request, *args, **kwargs):
        print(request.user.documentcopy_set.all().filter())
        self.extra_context = {'user_has_doc':
                                  len(request.user.documentcopy_set.all().filter(
                                      doc=Document.objects.get(id=int(request.path.replace('/', '')))))}
        return super().get(request, *args, **kwargs)





@need_logged_in
def checkout(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    user = request.user
    if user.is_staff:
        return Http404
    if user.documentcopy_set.filter(doc=doc):
        return redirect('/{0}/'.format(pk))
    if doc.copies > 0:
        doc.copies -= 1
        doc.save()
        if True or user.status == 'student':
            new_copy = DocumentCopy(doc=doc,
                                    checked_up_by_whom=user, returning_date=(
                    datetime.date.today() + datetime.timedelta(days=14)).strftime("%Y-%m-%d"))
        else:
            new_copy = DocumentCopy(doc=doc,
                                    checked_up_by_whom=user, returning_date=(
                    datetime.date.today() + datetime.timedelta(days=21)).strftime("%Y-%m-%d"))

        new_copy.save()
    return redirect('/{0}/'.format(pk))
