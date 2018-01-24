
from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView, DetailView

import datetime
from Documents.librarian_view import *


class IndexView(ListView):

    template_name = 'Documents/index.html'
    model = Document
    context_object_name = 'documents'
    paginate_by = 10

    def post(self, request):
        chosen_docs = [Document.objects.get(id=int(id)) for id in request.POST.keys() if id.isdigit()]
        if chosen_docs:
            for doc in chosen_docs:
                if doc.copies > 0:
                    doc.copies -= 1
                    doc.save()
                    user = request.user

                    if not user.is_anonymous:
                        if True or user.status == 'student':
                            new_copy = DocumentCopy(doc=doc,
                                                    checked_up_by_whom=user, returning_date=(
                                        datetime.date.today() + datetime.timedelta(days=14)).strftime("%Y-%m-%d"))
                        else:
                            new_copy = DocumentCopy(doc=doc,
                                                    checked_up_by_whom=user, returning_date=(
                                        datetime.date.today() + datetime.timedelta(days=21)).strftime("%Y-%m-%d"))

                        new_copy.save()
                    else:
                        return redirect('/user/login/')
        return redirect('/')


class DocumentDetail(DetailView):
    template_name = 'Documents/doc_inf.html'
    model = Document
    context_object_name = 'doc'

    def get_context_data(self, **kwargs):
        context = super(DocumentDetail, self).get_context_data(**kwargs)
        print(context)
        return context



def get_type_of_doc(doc_id):
    for t in Document.__subclasses__():
        try:
            t.objects.get(id=doc_id)
            return t.type
        except:
            pass
    return 'document'
