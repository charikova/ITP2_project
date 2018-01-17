from django.contrib import admin
from .models import Book, JournalArticle, AVFile

admin.site.register(Book)
admin.site.register(JournalArticle)
admin.site.register(AVFile)
