from django.views.generic import ListView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from Documents.librarian_view import *


class IndexView(ListView):
    """
    main page for browsing documents
    """
    template_name = 'Documents/index.html'
    model = Document
    context_object_name = 'documents'
    paginate_by = 15

    def get_queryset(self):
        get_request = self.request.GET

        # quick search
        if get_request.get('q') and get_request.get('q') != 'None':
            return Document.objects.filter(title__icontains=self.request.GET.get('q'))
        # expanded search
        elif any_search_criteria(get_request):
            model = determine_model(self.request.GET.get('type'))
            kwargs, exkwargs = dict(), dict()  # kwargs for filter query, exkwargs for exclude query
            args = list()  # args for filter query
            mo = '&' if get_request.get('match') == 'on' else '|'  # match operand (either OR or AND)

            # create db query considering match operand. Resulting query should consist of Q() objects splitted
            # by operands. For example if request contains title and keywords queries db_query will look like
            # 'Q(title__icontains=title_query) | Q(keywords_icontains=word1_from_keywords) |
            #  Q(keywords_icontains=word2_from_keywords)'
            db_query = Q()
            if get_request.get('authors') and get_request.get('authors') != "None":
                for word in get_request.get('authors').split():
                    if mo == '|':
                        db_query |= Q(authors__icontains=word)
                    else:
                        db_query &= Q(authors__icontains=word)
            if get_request.get('title') and get_request.get('title') != "None":
                for word in get_request.get('title').split():
                    if mo == '|':
                        db_query |= Q(title__icontains=word)
                    else:
                        db_query &= Q(title__icontains=word)
            if get_request.get('keywords') and get_request.get('keywords') != "None":
                for word in get_request.get('keywords').split():
                    if mo == '|':
                        db_query |= Q(keywords__icontains=word)
                    else:
                        db_query &= Q(keywords__icontains=word)

            args.append(db_query)

            if get_request.get('available') == 'on':  # by availability
                exkwargs['copies'] = 0
            if get_request.get('noref') == "on":
                exkwargs['is_reference'] = True
            if get_request.get('room') and get_request.get('room').isdigit():
                kwargs['room'] = int(get_request.get('room'))
            if get_request.get('level') and get_request.get('level').isdigit():
                kwargs['level'] = int(get_request.get('level'))
            return model.objects.filter(*args, **kwargs).exclude(**exkwargs).order_by('title')

        return Document.objects.order_by('title')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.request.GET.get('title', '')
        context['match'] = 'on' if self.request.GET.get('match') == 'on' else ''
        context['available'] = 'on' if self.request.GET.get('available') == 'on' else ''
        context['noref'] = 'on' if self.request.GET.get('noref') == 'on' else ''
        context['authors'] = self.request.GET.get('authors', '')
        context['room'] = self.request.GET.get('room')
        context['level'] = self.request.GET.get('level')
        context['q'] = self.request.GET.get('q', '')
        context['keywords'] = self.request.GET.get('keywords', '')
        context['types'] = [Type.type for Type in Document.__subclasses__()]
        if self.request.GET.get('type') in context['types']:
            context['default_type'] = self.request.GET.get('type')
            del context['types'][context['types'].index(self.request.GET.get('type'))]
            context['types'].append('All')
        else:
            context['default_type'] = 'All'
        return context


def document_detail(request, pk):
    """
    document details page. Find document via pk(id). Get all fields of the doc and show rendered doc_inf.html
    """
    doc = get_object_or_404(Document, pk=pk)
    for Type in Document.__subclasses__():
        if Type.objects.filter(pk=pk):
            doc = Type.objects.get(pk=pk)
    context = dict()
    context['doc'] = doc
    context['cover'] = doc.__dict__['cover']
    context['fields'] = list()  # rest of fields
    excess_fields = ['document_ptr_id', '_state', 'id', 'cover']
    if not request.user.is_staff:
        excess_fields += ['is_reference', 'is_bestseller', 'room', 'level', 'keywords']
    for key, value in doc.__dict__.items():
        if key not in excess_fields:
            context['fields'].append((key.replace('is', '').replace('_', " ").capitalize(), value))
    return render(request, 'Documents/doc_inf.html', context)


def determine_model(type):
    """
    Determines model by type
    :param type: string value which defined in every subclass of Document
    :return: model class which has type, Document model if nothing was found
    """
    model = Document
    for Type in Document.__subclasses__():
        if Type.type == type:
            model = Type
            break
    return model


def any_search_criteria(get_request):
    criteria = ['title', 'authors', 'keywords', 'room', 'level', 'type']
    for query, value in get_request.items():
        if query in criteria:
            if query == 'type' and value != "All":
                return True
            if query != 'type' and value and value != "None" and value != "False":
                return True
    return False


class CheckedOutDocsView(ListView):
    model = DocumentCopy
    template_name = 'Documents/checked_out_docs.html'
    context_object_name = 'document_copies'
    paginate_by = 20
