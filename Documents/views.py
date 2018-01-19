from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from .models import *

def index(request):
    documents = Paginator(Document.objects.all(), 10)
    chosen_docs = [Document.objects.get(id=int(id)) for id in request.POST.keys() if id.isdigit()]
    try:
        page_num = request.GET['page']
        if not documents.page(page_num):
            raise EmptyPage
    except (KeyError, EmptyPage):
        page_num = 1
    print(chosen_docs)
    return render(request, 'Documents/index.html', {'documents': documents.page(page_num)})


def show_doc_inf(request, doc_id):
    return render(request, 'Documents/doc_inf.html', {'doc': Document.objects.get(id=doc_id)})
