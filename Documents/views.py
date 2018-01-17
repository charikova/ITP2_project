from django.http import HttpResponse
from .models import *

def s(request):
    http = "List of all documents: <br>"
    documents = Document.objects.all()
    for d in documents:
        url = '/documents/' + str(d.id) + "/"
        http += '<a href="{}">{}</a><br>'.format(url, d.title)
    return HttpResponse(http)


def show_doc_inf(request, doc_id):
    print("dsfasdfasdgasdklfja;dlsdnrivweubioebio;weurviowervbioaeua;")
    print(doc_id)
    http = Document.objects.filter(id=doc_id)
    print(http)
    return HttpResponse(http)
