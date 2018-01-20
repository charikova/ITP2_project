from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from .models import *
from UserCards import models as user_cards_models
from django.http import HttpResponse
from django.shortcuts import render_to_response

def index(request):
    documents = Paginator(Document.objects.all(), 2)
    chosen_docs = [Document.objects.get(id=int(id)) for id in request.POST.keys() if id.isdigit()]
    try:
        page_num = request.GET['page']
        if not documents.page(page_num):
            raise EmptyPage
    except (KeyError, EmptyPage):
        page_num = 1
    if chosen_docs:
        for doc in chosen_docs:
            if doc.copies > 0:
                doc.copies -= 1
                doc.save()
                try:
                    holder = user_cards_models.UserCard.objects.get(session_id=request.COOKIES['sessionid'])
                    new_copy = DocumentCopy(doc=doc,
                    checked_up_by_whom=holder)
                    new_copy.save()
                except:
                    return HttpResponse("You are not currently logged in")
    response = render(request, 'Documents/index.html', {'documents': documents.page(page_num)})
    return response


def show_doc_inf(request, doc_id):
    doc = Document.objects.get(id=doc_id)
    type = get_type_of_doc(doc_id)
    print(type)
    return render(request, 'Documents/doc_inf.html', {'doc': doc, 'type': type})

def get_type_of_doc(doc_id):
    for t in Document.__subclasses__():
        try:
            t.objects.get(id=doc_id)
            return t.type
        except:
            pass
    return 'document'

