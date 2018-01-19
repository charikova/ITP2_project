from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from .models import *
from UserCards import models as user_cards_models

def index(request):
    documents = Paginator(Document.objects.all(), 10)
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
                new_copy = DocumentCopy(doc=doc,
                    checked_up_by_whom=user_cards_models.UserCard.objects.get(session_id=request.COOKIES['sessionid']))
                new_copy.save()
    response = render(request, 'Documents/index.html', {'documents': documents.page(page_num)})
    return response


def show_doc_inf(request, doc_id):
    return render(request, 'Documents/doc_inf.html', {'doc': Document.objects.get(id=doc_id)})
