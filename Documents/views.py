from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, Http404
import datetime
from Documents.librarian_view import *


class IndexView(ListView):
    """
    main page for browsing documents
    """
    template_name = 'Documents/index.html'
    model = Document
    context_object_name = 'documents'
    paginate_by = 10


def document_detail(request, pk):
    """
    document details page. Find document via pk(id). Get all fields of the doc and show rendered doc_inf.html
    """
    doc = get_object_or_404(Document, pk=pk)
    for Type in Document.__subclasses__():
        if Type.objects.filter(pk=pk):
            doc = Type.objects.get(pk=pk)
    context = dict()
    if not request.user.is_anonymous:
        context['user_has_doc'] = len(request.user.documentcopy_set.all().filter(
                doc=Document.objects.get(id=int(request.path.replace('/', ''))))) # args that will be sent to doc_inf.html
    context['doc'] = doc
    context['cover'] = doc.__dict__['cover']
    context['fields'] = list() # rest of fields
    excess_fields = ['document_ptr_id', '_state', 'id', 'cover', 'keywords']
    for key, value in doc.__dict__.items():
        if key not in excess_fields:
            context['fields'].append((key.replace('_', " ").capitalize(), value))
    return render(request, 'Documents/doc_inf.html', context)


@need_logged_in
def checkout(request, pk):
    """
    when user check out doc -> find this doc via pk(id), create an instance of document_copy
    which will be linked to this document and to user
    """
    doc = get_object_or_404(Document, pk=pk)
    user = request.user
    if user.is_staff:
        raise Http404('staff can not take documents')
    if doc.is_reference:
        raise Http404("reference book can not be checked out")
    if user.documentcopy_set.filter(doc=doc): # if user already has this doc
        return redirect('/{0}/'.format(pk))
    if doc.copies > 0:
        doc.copies -= 1
        doc.save()
        days = 21 # for student
        if doc.type == "AVFile" or doc.type == "JournalArticle":
            days = 14
        elif user.userprofile.status == 'faculty':
            days = 28
        elif doc.is_bestseller:
            days = 14
        new_copy = DocumentCopy(doc=doc,
                                checked_up_by_whom=user, returning_date=(
                datetime.date.today() + datetime.timedelta(days=days)).strftime("%Y-%m-%d"))

        new_copy.save()
    return redirect('/{0}/'.format(pk)) # go back to doc page
