from django.db import models
from django.contrib.auth.models import User
import datetime

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
    type = models.CharField(max_length=100, default='Document')

    def __str__(self):
        return "{}; authors: {}".format(self.title, self.price, self.authors)


class Book(Document):
    publisher = models.CharField(max_length=250, blank=True)
    edition = models.PositiveIntegerField(default=1)
    publication_date = models.DateField(max_length=250, blank=True)
    type = 'Book'


class JournalArticle(Document):
    publisher_journal = models.CharField(max_length=250, blank=True)
    editors = models.CharField(max_length=250, blank=True)
    publication_date = models.DateField(max_length=250, blank=True)
    type = 'JournalArticle'


class AVFile(Document):
    type = 'AVFile'


class DocumentCopy(models.Model):
    """
    copy object which is created when user checked out document
    """
    doc = models.ForeignKey(Document, blank=True, default=None, on_delete=models.CASCADE) # link document which is checked out
    checked_up_by_whom = models.ForeignKey(User, blank=True, default=None, on_delete=models.CASCADE) # link to holder
    date = models.DateTimeField(default=str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M")))
    returning_date = models.DateTimeField(default=str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M")))
    time_left = models.CharField(null=True, max_length=250)
    level = models.PositiveIntegerField(default=1)
    room = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.doc)

