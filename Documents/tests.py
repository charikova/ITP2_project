from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpRequest
from .models import *
from Documents.views import checkout
import datetime
from UserCards.models import UserProfile
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
        # initial state
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
        pass

    def TC3(self):
        self.assertIs()

    def TC4(self):
        f = User.objects.create_user('Faculty', 'fac@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=f, status='faculty', phone_number=896000, address='2-107')

        s = User.objects.create_user('Student', 'stu@mail.ru', '123456qwerty', first_name='S', last_name='L')
        UserProfile.objects.create(user=s, status='student', phone_number=796001, address='2-110')

        #l = UserProfile.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L', /
                        # is_stuff=True)
        b = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub', is_bestseller=True)

        request = HttpRequest()
        request.method = 'GET'
        request.user = f
        checkout(request, b.id)

        self.assertEqual(
            (f.documentcopy_set.filter(doc=b)[0].returning_date - f.documentcopy_set.filter(doc=b)[0].date).days,
            datetime.timedelta(days=14).days-1)

    def TC5(self):
        s1 = User.objects.create_user('Student1', 'Student1@mail.ru', '123456qwerty', first_name='Student1', last_name='L')
        s2 = User.objects.create_user('Student2', 'Student2@mail.ru', '123456qwerty', first_name='Student2', last_name='L')
        s3 = User.objects.create_user('Student3', 'Student3@mail.ru', '123456qwerty', first_name='Student3', last_name='L')

        UserProfile.objects.create(user=s1, status='student', phone_number=896000, address='2-107')
        UserProfile.objects.create(user=s2, status='student', phone_number=896000, address='2-107')
        UserProfile.objects.create(user=s3, status='student', phone_number=896000, address='2-107')

        #l = User.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L',/
                                     #is_stuff=True)

        b = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub', is_bestseller=True)

        request = HttpRequest()
        request.method = 'GET'
        request.user = s1
        checkout(request, b.id)

        request.user = s2
        checkout(request, b.id)

        request.user = s3
        checkout(request, b.id)

        self.assertEqual(len(b.documentcopy_set.all()), 2)

    def TC6(self):
        p = User.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=p, status='student', phone_number=896000, address='2-107')

        # l = User.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L', /
                                     # is_stuff=True)
        b = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub', is_bestseller=True)

        request = HttpRequest()
        request.method = 'GET'
        request.user = p
        checkout(request, b.id)
        checkout(request, b.id)

        self.assertEqual(len(b.documentcopy_set.all()), 1)




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
