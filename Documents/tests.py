from django.test import TestCase
from UserCards.models import UserProfile
from django.http import HttpRequest, Http404
from .models import *
from Documents.views import checkout
import datetime
from UserCards.views import user_card_info


class IntroductionToProgrammingTestCase(TestCase):

    def TC1(self):
        #initial state
        p = User.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        b = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub')
        self.assertEqual(b.copies, 2, msg="not 2 copies")

        request = HttpRequest()
        request.method = 'GET'
        request.user = p
        checkout(request, b.id)

        patron_has_one_copy = len(p.documentcopy_set.filter(doc=b)) == 1
        library_has_one_copy = len(Document.objects.filter(title='title')) == 1
        self.assertIs(patron_has_one_copy, True)
        self.assertIs(library_has_one_copy, True)


    def TC2(self):
        p = User.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')

        # doesn't have any books by author A
        have_book = len(Book.objects.filter(authors='A')) > 0
        self.assertEqual(have_book, False)

        # patron checks out book by A
        request = HttpRequest()
        request.method = "GET"
        request.user = p

        try:
            checkout(request, 1000) # 1000 id doesn't exist
        except Http404:
            pass
        else:
            raise Exception('should raise 404')


    def TC3(self):
        student = User.objects.create_user('s', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        faculty = User.objects.create_user('f', 'exampl2@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=student, phone_number=123, status='student', address='1-103')
        UserProfile.objects.create(user=faculty, phone_number=123, status='faculty', address='1-103')
        book = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub')

        request = HttpRequest()
        request.method = "GET"
        request.user = faculty
        checkout(request, book.id)

        returning_date = faculty.documentcopy_set.get(doc=book).returning_date
        should_be_today = returning_date - datetime.timedelta(days=28)
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertEqual(should_be_today, datetime.date.today())

    def TC4(self):
        pass


    def TC5(self):
        pass


    def TC6(self):
        pass


    def TC7(self):
        pass


    def TC8(self):
        pass


    def TC9(self):
        pass


    def TC10(self):
        pass


