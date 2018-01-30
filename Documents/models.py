from django.db import models
import uuid
from UserCards import models as user_cards_models
from django.contrib.auth.models import User
import datetime
from django.urls import reverse

class Document(models.Model):
    '''
    Base class for all documents
    '''
    title = models.CharField(max_length=250)
    price = models.IntegerField()
    keywords = models.CharField(max_length=250) # the list of keywords stored in string
                                        # splitted by space "k1 k2 k3" (e.g. 'Programming Language')
    authors = models.CharField(max_length=250) # the list of authors in string format splitted by space
    cover = models.CharField(max_length=1000, default="https://lh3.googleusercontent.com/zqfUbCXdb1oGmsNEzNxTjQU5ZlS3x46nQoB83sFbRSlMnpDTZgdVCe_LvCx-rl7sOA=w300")
    copies = models.PositiveIntegerField(default=1)
    room = models.PositiveIntegerField(default=1)
    level = models.PositiveIntegerField(default=1)
    type = models.CharField(max_length=100, default='Document')

    def __str__(self):
        return "title: {}; price: {}; authors: {}".format(self.title, self.price, self.authors)


class Book(Document):
    publisher = models.CharField(max_length=250)
    edition = models.PositiveIntegerField(default=1)
    publication_date = models.DateField(max_length=250)
    type = 'Book'


class JournalArticle(Document):
    publisher_journal = models.CharField(max_length=250)
    editors = models.CharField(max_length=250)
    publication_date = models.DateField(max_length=250)
    type = 'JournalArticle'


class AVFile(Document):
    type = 'AVFile'


class DocumentCopy(models.Model):
    doc = models.ForeignKey(Document, null=True, default=None, on_delete=models.CASCADE)
    checked_up_by_whom = models.ForeignKey(User, null=True, default=None, on_delete=models.CASCADE)
    date = models.DateTimeField(default=str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M")))
    returning_date = models.DateTimeField(default=str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M")))
    time_left = models.CharField(null=True, max_length=250)

    def __str__(self):
        return str(self.doc)


class BookRequest(models.Model):
    doc = models.ForeignKey(Document, null=True, default=None, on_delete=models.CASCADE)
    checked_up_by_whom = models.ForeignKey(User, null=True, default=None, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book_request")

    def get_absolute_url(self):
        return reverse('request-detail', args=[str(self.id)])








































'''
Don't delete this peace of code!!! Otherwise db crashes. 
Don't either ask me why ¯\_(ツ)_/¯
'''
class Copy(Document):
    pass