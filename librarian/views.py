from django.shortcuts import render
from django.views.generic import ListView
from Documents.models import Document


class IndexView(ListView):
    model = Document
    template_name = 'librarian/index.html'
    paginate_by = 2
