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
    paginate_by = 10

    def get_queryset(self):
        if self.request.GET:
            model = determine_model(self.request.GET.get('type'))
            kwargs, exkwargs = dict(), dict()
            args, exargs = list(), list()

            get_request = self.request.GET
            containing = ('' if get_request.get('case') else 'i') + 'contains'

            if get_request.get('match'):
                if get_request.get('authors'):  # by author
                    kwargs['authors__' + containing] = get_request.get('authors')
                if get_request.get('keywords'): # by keywords
                    kwargs['keywords__' + containing] = get_request.get('keywords')
                if get_request.get('title'):    # by title
                    kwargs['title__' + containing] = get_request.get('title')
            else:
                exec('args.append(Q() {0} {1} {2})'.format(
                    "| Q(**{'authors__' + containing: get_request.get('authors')})" if get_request.get('authors') else "",
                    "| Q(**{'keywords__' + containing: get_request.get('keywords')})" if get_request.get('keywords') else "",
                    "| Q(**{'title__' + containing: get_request.get('title')})" if get_request.get('title') else ""
                ))
            if get_request.get('available'):  # by availability
                exkwargs['copies'] = 0
            if get_request.get('room'):
                kwargs['room'] = int(get_request.get('room'))
            if get_request.get('level'):
                kwargs['level'] = int(get_request.get('level'))
            return model.objects.filter(*args, **kwargs).exclude(*exargs, **exkwargs)
        return super(IndexView, self).get_queryset()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = self.request.GET.get('case')
        context['title'] = self.request.GET.get('title')
        context['q'] = self.request.GET.get('q')
        context['available'] = self.request.GET.get('available')
        context['match'] = self.request.GET.get('match')
        context['authors'] = self.request.GET.get('authors')
        context['room'] = self.request.GET.get('room')
        context['level'] = self.request.GET.get('level')
        context['keywords'] = self.request.GET.get('keywords')
        context['types'] = [Type.type for Type in Document.__subclasses__()]
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
