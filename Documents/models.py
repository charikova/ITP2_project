from django.db import models


class Document(models.Model):
    '''
    Base class for all documents
    '''
    title = models.CharField(max_length=250)
    checked_up = models.BooleanField()
    checked_up_by_whom = models.CharField(max_length=250)
    price = models.IntegerField()
    keywords = models.CharField(max_length=250) # the list of keywords stored in string
                                        # splitted by space "k1 k2 k3" (e.g. 'Programming Language')
    authors = models.CharField(max_length=250) # the list of authors in string format splitted by space
    cover = models.CharField(max_length=1000)
    checking_time = models.IntegerField()

    def __str__(self):
        return "title: {}; price: {}; authors: {}".format(self.title, self.price, self.authors)


class Book(Document):
    publisher = models.CharField(max_length=250)
    edition = models.IntegerField()
    publication_date = models.CharField(max_length=250)


class JournalArticle(Document):
    publisher_journal = models.CharField(max_length=250)
    editors = models.CharField(max_length=250)
    publication_date = models.CharField(max_length=250)


class AVFile(Document):
    pass


class Copy(Document):
    document = models.ForeignObject(Document)



