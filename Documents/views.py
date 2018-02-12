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
    paginate_by = 5

    def get_queryset(self):
        if self.request.GET:
            model = determine_model(self.request.GET.get('type'))
            kwargs, exkwargs = dict(), dict()
            args, exargs = list(), list()
            get_request = self.request.GET
            print(get_request)
            mo = '&' if get_request.get('match') == 'on' else '|'
            # try add all search criteria (e.g. by title) if this criteria was sent in get request
            exec('args.append(Q() {0} {1} {2})'.format(
                mo+" Q(**{'authors__icontains': get_request.get('authors')})" if get_request.get('authors') != "None" else "",
                mo+"Q(**{'keywords__icontains': get_request.get('keywords')})" if get_request.get('keywords') != "None" else "",
                mo+"Q(**{'title__icontains': get_request.get('title')})" if get_request.get('title') != "None" else ""
            ))
            if get_request.get('available') == 'on':  # by availability
                exkwargs['copies'] = 0
            if get_request.get('room') and get_request.get('room').isdigit():
                kwargs['room'] = int(get_request.get('room'))
            if get_request.get('level') and get_request.get('level').isdigit():
                kwargs['level'] = int(get_request.get('level'))
            return model.objects.filter(*args, **kwargs).exclude(*exargs, **exkwargs)
        return Document.objects.order_by('title')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('title') != "None":
            context['title'] = self.request.GET.get('title')
        context['match'] = self.request.GET.get('match') == 'on'
        context['available'] = self.request.GET.get('available') == 'on'
        if self.request.GET.get('authors') != "None":
            context['authors'] = self.request.GET.get('authors')
        context['room'] = self.request.GET.get('room')
        context['level'] = self.request.GET.get('level')
        if self.request.GET.get('keywords') != "None":
            context['keywords'] = self.request.GET.get('keywords')
        context['types'] = [Type.type for Type in Document.__subclasses__()]
        if self.request.GET.get('type') in context['types']:
            context['default_type'] = self.request.GET.get('type')
            del context['types'][context['types'].index(self.request.GET.get('type'))]
            context['types'].append('All')
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
