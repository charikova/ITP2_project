from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpRequest
from .models import *
from Documents.views import checkout
from UserCards.views import user_card_info


class IntroductionToProgrammingTestCase(TestCase):


    def TC1(self):
        #initial state
        p = User.objects.get(name='gnomer')
        b = Book.objects.get(title='testbook')

        request = HttpRequest()
        request.method = 'GET'
        request.REMOTE_USER = p
        checkout(request, b.id)

        patron_has_one_copy = len(p.documentcopy_set.filter(title='testbook')) == 1
        library_has_one_copy = len(Document.objects.filter(title='testbook')) == 1
        self.assertIs(patron_has_one_copy, True)
        self.assertIs(library_has_one_copy, True)


    def TC2(self):
        self.assertIs()


    def TC3(self):
        self.assertIs()


    def TC4(self):
        self.assertIs()


    def TC5(self):
        self.assertIs()


    def TC6(self):
        self.assertIs()


    def TC7(self):
        self.assertIs()


    def TC8(self):
        self.assertIs()


    def TC9(self):
        self.assertIs()


    def TC10(self):
        self.assertIs()
