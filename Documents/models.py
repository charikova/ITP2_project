from django.db import models
from UserCards import models as user_cards_models

class Document(models.Model):
    '''
    Base class for all documents
    '''
    title = models.CharField(max_length=250)
    price = models.IntegerField()
    keywords = models.CharField(max_length=250) # the list of keywords stored in string
                                        # splitted by space "k1 k2 k3" (e.g. 'Programming Language')
    authors = models.CharField(max_length=250) # the list of authors in string format splitted by space
    cover = models.CharField(max_length=1000)
    checking_time = models.IntegerField()
    copies = models.PositiveIntegerField(default=1)

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


class DocumentCopy(models.Model):
    doc = models.ForeignKey(Document, null=True, default=None, on_delete=models.CASCADE)
    checked_up_by_whom = models.ForeignKey(user_cards_models.UserCard, null=True, default=None, on_delete=models.CASCADE)






































'''
Don't delete this peace of code!!! Otherwise db crashes. 
Don't ask me why ¯\_(ツ)_/¯
'''
class Copy(Document):
    pass