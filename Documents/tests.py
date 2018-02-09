from django.test import TestCase
from UserCards.models import UserProfile
from django.http import HttpRequest, Http404
from .models import *
from Documents.views import checkout
import datetime
from UserCards.views import user_card_info


class TC(TestCase):

    def test_TC1(self):
        #initial state
        p = User.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=p, phone_number=123, status='student', address='1-103')
        l = User.objects.create_user('username2', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L', is_staff=True)
        UserProfile.objects.create(user=l, phone_number=123, status='student', address='1-103')
        b = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub')
        self.assertEqual(b.copies, 2)

        request = HttpRequest()
        request.method = 'GET'
        request.user = p
        checkout(request, b.id)

        patron_has_one_copy = len(p.documentcopy_set.filter(doc=b)) == 1
        library_has_one_copy = len(Document.objects.filter(title='title')) == 1
        self.assertIs(patron_has_one_copy, True)
        self.assertIs(library_has_one_copy, True)

        # librarian see
        request = HttpRequest()
        request.method = "GET"
        request.user = l
        request.path = '/user/?id=' + str(p.id) # sees patron's page
        response = user_card_info(request)
        self.assertEqual(response.status_code, 200) # librarian has access to see this page
        self.assertEqual(b.title in str(response.content), True) # there are exist title of this book in response content


    def test_TC2(self):
        #library has patron and librarian
        p = User.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',
                                             is_staff=True)
        UserProfile.objects.create(user=librarian, phone_number=123, status='faculty', address='1-103')

        # doesn't have any books by author A
        have_book = len(Book.objects.filter(authors='A')) > 0
        self.assertEqual(have_book, False)

        request = HttpRequest()
        request.method = "GET"
        request.user = p
        try:
            checkout(request, 1000) # 1000 id doesn't exist (user tries to checkout book that doesn't exist)
        except Http404: # expected state: 404 error
            pass
        else:
            raise Exception('should raise 404')


    def test_TC3(self):
        # library has s, f, l and book b
        student = User.objects.create_user('s', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        faculty = User.objects.create_user('f', 'exampl2@mail.ru', '123456qwerty', first_name='F', last_name='L')
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L', is_staff=True)
        UserProfile.objects.create(user=student, phone_number=123, status='student', address='1-103')
        UserProfile.objects.create(user=faculty, phone_number=123, status='faculty', address='1-103')
        UserProfile.objects.create(user=librarian, phone_number=123, status='faculty', address='1-103')
        # book
        book = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub')

        # faculty checks out book
        request = HttpRequest()
        request.method = "GET"
        request.user = faculty
        checkout(request, book.id)

        # faculty has 4 weeks to return this book since today
        returning_date = faculty.documentcopy_set.get(doc=book).returning_date
        should_be_today = returning_date - datetime.timedelta(days=28) # 4 weeks = 28 days
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)

        self.assertEqual(should_be_today, datetime.date.today())

    def test_TC4(self):
        #
        f = User.objects.create_user('Faculty', 'fac@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=f, status='faculty', phone_number=896000, address='2-107')

        s = User.objects.create_user('Student', 'stu@mail.ru', '123456qwerty', first_name='S', last_name='L')
        UserProfile.objects.create(user=s, status='student', phone_number=796001, address='2-110')

        b = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub', is_bestseller=True)

        request = HttpRequest()
        request.method = 'GET'
        request.user = f
        checkout(request, b.id)

        returning_date = f.documentcopy_set.get(doc=b).returning_date
        should_be_today = returning_date - datetime.timedelta(days=28) # day or returning minus 28 days
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)

        self.assertEqual(should_be_today, datetime.date.today())

    def test_TC5(self):
        s1 = User.objects.create_user('Student1', 'Student1@mail.ru', '123456qwerty', first_name='Student1',
                                      last_name='L')
        s2 = User.objects.create_user('Student2', 'Student2@mail.ru', '123456qwerty', first_name='Student2',
                                      last_name='L')
        s3 = User.objects.create_user('Student3', 'Student3@mail.ru', '123456qwerty', first_name='Student3',
                                      last_name='L')

        UserProfile.objects.create(user=s1, status='student', phone_number=896000, address='2-107')
        UserProfile.objects.create(user=s2, status='student', phone_number=896000, address='2-107')
        UserProfile.objects.create(user=s3, status='student', phone_number=896000, address='2-107')

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
        self.assertEqual(len(s1.documentcopy_set.filter(doc=b)), 1) # s1 has b
        self.assertEqual(len(s2.documentcopy_set.filter(doc=b)), 1) # s2 has b
        self.assertEqual(len(s3.documentcopy_set.filter(doc=b)), 0) #  s3 has no b

    def test_TC6(self):
        p = User.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=p, status='student', phone_number=896000, address='2-107')
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L', is_staff=True)

        b = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub', is_bestseller=True)

        request = HttpRequest()
        request.method = 'GET'
        request.user = p
        checkout(request, b.id) # check it out twice
        checkout(request, b.id)

        self.assertEqual(len(b.documentcopy_set.all()), 1)

    def test_TC7(self):
        p1 = User.objects.create_user('s', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        p2 = User.objects.create_user('f', 'exampl2@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=p1, phone_number=123, status='student', address='1-103')
        UserProfile.objects.create(user=p2, phone_number=123, status='student', address='1-103')

        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',is_staff=True)
        UserProfile.objects.create(user=librarian, phone_number=123, status='faculty', address='1-103')

        b1 = Book.objects.create(title='b1', price=0, publication_date=datetime.datetime.now(),
                                   edition=1, copies=2, authors='sadf', cover='cover', publisher='pub')

        request = HttpRequest()
        request.method = "GET"
        request.user = p1
        checkout(request, b1.id)

        request = HttpRequest()
        request.method = "GET"
        request.user = p2
        checkout(request, b1.id)

        p1_has_one_copy = len(p1.documentcopy_set.filter(doc=b1)) == 1
        p2_has_one_copy = len(p2.documentcopy_set.filter(doc=b1)) == 1
        p1_and_p2 = p1_has_one_copy == p2_has_one_copy
        library_has_no_copy = len(Document.objects.filter(title='title')) == 0

        self.assertEqual(p1_and_p2, library_has_no_copy)

    def test_TC8(self):
        student = User.objects.create_user('s', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        faculty = User.objects.create_user('f', 'exampl2@mail.ru', '123456qwerty', first_name='F', last_name='L')
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',
                                             is_staff=True)

        UserProfile.objects.create(user=student, phone_number=123, status='student', address='1-103')
        UserProfile.objects.create(user=faculty, phone_number=123, status='faculty', address='1-103')
        UserProfile.objects.create(user=librarian, phone_number=123, status='faculty', address='1-103')

        book = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                   edition=1, copies=2, authors='sadf', cover='cover', publisher='pub')
        request = HttpRequest()
        request.method = "GET"
        request.user = student
        checkout(request, book.id)

        returning_date = student.documentcopy_set.get(doc=book).returning_date
        should_be_today = returning_date - datetime.timedelta(days=21)
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)

        self.assertEqual(should_be_today, datetime.date.today())

    def test_TC9(self):

        # The library has at least one patron (Faculty) 'f' and one patron (Student) 's', and a librarian. It also has book 'b'
        # that is best seller
        student = User.objects.create_user('s', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=student, phone_number=123, status='student', address='1-103')
        faculty = User.objects.create_user('f', 'exampl2@mail.ru', '123456qwerty', first_name='F', last_name='L')
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',
                                             is_staff=True)

        book = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                   edition=1, copies=1, authors='sadf', cover='cover', publisher='pub', is_bestseller=True)

        # 's' checks out book 'b'
        request = HttpRequest()
        request.method = "GET"
        request.user = student
        checkout(request, book.id)

        # The book is checked out by 's' with returning time of 2 weeks (from the day it was checked out)
        returning_date = student.documentcopy_set.get(doc=book).returning_date
        should_be_today = returning_date - datetime.timedelta(days=14)
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)

        self.assertEqual(should_be_today, datetime.date.today())

    def test_TC10(self):

        # There is at least one patron and one librarian in the system. The library has one book A and one reference book B
        student = User.objects.create_user('s', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=student, phone_number=123, status='student', address='1-103')

        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',
                                             is_staff=True)
        UserProfile.objects.create(user=librarian, phone_number=123, status='librarian', address='1-103')

        A = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                   edition=1, copies=1, authors='sadf', cover='cover', publisher='pub')

        B = Book.objects.create(title='title2', price=0, publication_date=datetime.datetime.now(),
                                   edition=1, copies=1, authors='sadf', cover='cover', publisher='pub',
                                   is_reference=True)

        # The patron tries to check out the book A and reference book B.
        request = HttpRequest()
        request.method = "GET"
        request.user = student
        checkout(request, A.id) # everything ok

        try:
            checkout(request, B.id) # try to checkout reference book
        except Http404: # expected state: 404 error
            pass
        else:
            raise Exception('should be 404')

        # The system allows to check out only the book A. The reference book B is not available for checking out
        number_copies_patron_has = len(student.documentcopy_set.all())
        self.assertEqual(number_copies_patron_has, 1)

        student.documentcopy_set.get(id=A.id) # will raise error if copy of A doesn't exist



