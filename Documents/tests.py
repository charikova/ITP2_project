from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpRequest
from .models import *
from Documents.views import checkout
import datetime
from UserCards.views import user_card_info


class UserGenerator:
    username = 'username'
    first_name = 'first_name'
    last_name = 'last_name'
    email = 'example@mail.com'

    @staticmethod
    def _get_user():
        user = User()
        user.username = UserGenerator.username
        user.first_name = UserGenerator.first_name
        user.last_name = UserGenerator.last_name
        user.email = UserGenerator.email
        user.set_password('1234567890qwerty')
        user.save()
        return user

    @staticmethod
    def get_student():
        user = UserGenerator._get_user()
        user.status = 'student'

    @staticmethod
    def get_faculty():
        user = UserGenerator._get_user()
        user.status = 'faculty'

    @staticmethod
    def get_librarian():
        user = UserGenerator._get_user()
        user.status = 'librarian'
        user.is_staff = True


class DocGenerator:
    title = 'title'
    cover = 'cover'
    authors = 'authors'
    price = 0
    copies = 1

    @staticmethod
    def get_book():
        b = Book()
        b.title = DocGenerator.title
        b.cover = DocGenerator.cover
        b.authors = DocGenerator.authors
        b.price = DocGenerator.price
        b.copies = DocGenerator.copies
        b.publication_date = datetime.datetime.now()
        b.publisher = 'unknown'
        b.edition = 1
        b.type = 'Book'
        b.save()
        return b

    @staticmethod
    def get_avfile():
        f = AVFile()
        f.type = 'AVFile'
        f.save()
        return f

    @staticmethod
    def get_article():
        b = JournalArticle()
        b.publication_date = datetime.datetime.now()
        b.publisher_journal = 'unknown'
        b.edition = 1
        b.type = 'JournalArticle'
        b.save()
        return b


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
        b = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub')




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


if __name__ == "__main__":
    itptest = IntroductionToProgrammingTestCase()
    itptest.TC1()
