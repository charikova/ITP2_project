from django.http import HttpResponse
from django.shortcuts import render
from .models import *

def index(request):
    documents = Document.objects.all()
    print(request.POST)
    return render(request, 'Documents/index.html', {'documents': documents})


def show_doc_inf(request, doc_id):
    http = Document.objects.filter(id=doc_id)
    print(http)
    return HttpResponse(http)
