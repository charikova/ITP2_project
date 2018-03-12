from django.test import TestCase, Client

from BookRequests.models import Request
from UserCards.models import UserProfile
from django.http import HttpRequest, Http404, QueryDict
from .models import *
from BookRequests.views import make_new, approve_request
import BookRequests
from Documents import librarian_view
import datetime
import subprocess
from UserCards.views import user_card_info
from django.utils import timezone


class Delivery1(TestCase):

    def test_TC1(self):
        #  initial state
        p = User.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=p, phone_number=123, status='student', address='1-103')
        l = User.objects.create_user('username2', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L',
                                     is_staff=True)
        UserProfile.objects.create(user=l, phone_number=123, status='librarian', address='1-103')
        b = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub')
        self.assertEqual(b.copies, 2)

        request = HttpRequest()
        request.GET['doc'] = b.id
        request.user = p
        make_new(request)

        request.GET['user_id'] = p.id
        request.GET['req_id'] = p.request_set.get(doc=b).id
        request.user = l
        approve_request(request)

        patron_has_one_copy = len(p.documentcopy_set.filter(doc=b)) == 1
        library_has_one_copy = len(Document.objects.filter(title='title')) == 1
        self.assertIs(patron_has_one_copy, True)
        self.assertIs(library_has_one_copy, True)

        # librarian see
        request = HttpRequest()
        request.method = "GET"
        request.user = l
        request.GET['id'] = p.id
        response = user_card_info(request)
        self.assertEqual(response.status_code, 200)  # librarian has access to see this page
        self.assertEqual(b.title in str(response.content),
                         True)  # there are exist title of this book in response content

    def test_TC2(self):
        # library has patron and librarian
        p = User.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',
                                             is_staff=True)
        UserProfile.objects.create(user=librarian, phone_number=123, status='faculty', address='1-103')

        # doesn't have any books by author A
        have_book = len(Book.objects.filter(authors='A')) > 0
        self.assertEqual(have_book, False)

        request = HttpRequest()
        request.GET['doc'] = 1000  # 1000 id doesn't exist (user tries to checkout book that doesn't exist)
        request.user = p
        try:
            make_new(request)
        except Http404:  # expected state: 404 error
            pass
        else:
            raise Exception('should raise 404')

    def test_TC3(self):
        # library has s, f, l and book b
        student = User.objects.create_user('s', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        faculty = User.objects.create_user('f', 'exampl2@mail.ru', '123456qwerty', first_name='F', last_name='L')
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',
                                             is_staff=True)
        UserProfile.objects.create(user=student, phone_number=123, status='student', address='1-103')
        UserProfile.objects.create(user=faculty, phone_number=123, status='faculty', address='1-103')
        UserProfile.objects.create(user=librarian, phone_number=123, status='faculty', address='1-103')
        # book
        book = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                   edition=1, copies=2, authors='sadf', cover='cover', publisher='pub')

        # faculty checks out book
        request = HttpRequest()
        request.GET['doc'] = book.id
        request.user = faculty
        make_new(request)

        request.GET['user_id'] = faculty.id
        request.GET['req_id'] = faculty.request_set.get(doc=book).id
        request.user = librarian
        approve_request(request)

        # faculty has 4 weeks to return this book since today
        returning_date = faculty.documentcopy_set.get(doc=book).returning_date
        should_be_today = returning_date - datetime.timedelta(days=28)  # 4 weeks = 28 days
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)

        self.assertEqual(should_be_today, datetime.date.today())

    def test_TC4(self):
        #
        f = User.objects.create_user('Faculty', 'fac@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=f, status='faculty', phone_number=896000, address='2-107')

        s = User.objects.create_user('Student', 'stu@mail.ru', '123456qwerty', first_name='S', last_name='L')
        UserProfile.objects.create(user=s, status='student', phone_number=796001, address='2-110')

        l = User.objects.create_user('Librarian', 'stu@mail.ru', '123456qwerty', first_name='S', last_name='L',
                                     is_staff=True)
        UserProfile.objects.create(user=l, status='librarian', phone_number=796001, address='2-110')

        b = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub', is_bestseller=True)

        request = HttpRequest()
        request.GET['doc'] = b.id
        request.user = f
        make_new(request)

        request.GET['user_id'] = f.id
        request.GET['req_id'] = f.request_set.get(doc=b).id
        request.user = l
        approve_request(request)

        returning_date = f.documentcopy_set.get(doc=b).returning_date
        should_be_today = returning_date - datetime.timedelta(days=28)  # day or returning minus 28 days
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)

        self.assertEqual(should_be_today, datetime.date.today())

    def test_TC5(self):
        s1 = User.objects.create_user('Student1', 'Student1@mail.ru', '123456qwerty', first_name='Student1',
                                      last_name='L')
        s2 = User.objects.create_user('Student2', 'Student2@mail.ru', '123456qwerty', first_name='Student2',
                                      last_name='L')
        s3 = User.objects.create_user('Student3', 'Student3@mail.ru', '123456qwerty', first_name='Student3',
                                      last_name='L')
        l = User.objects.create_user('Librarian', 'Student3@mail.ru', '123456qwerty', first_name='Student3',
                                     last_name='L', is_staff=True)

        UserProfile.objects.create(user=s1, status='student', phone_number=896000, address='2-107')
        UserProfile.objects.create(user=s2, status='student', phone_number=896000, address='2-107')
        UserProfile.objects.create(user=s3, status='student', phone_number=896000, address='2-107')

        b = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub', is_bestseller=True)

        request = HttpRequest()
        request.GET['doc'] = b.id
        request.user = s1
        make_new(request)

        request.GET['user_id'] = s1.id
        request.GET['req_id'] = s1.request_set.get(doc=b).id
        request.user = l
        approve_request(request)

        request.user = s2
        make_new(request)
        request.GET['user_id'] = s2.id
        request.GET['req_id'] = s2.request_set.get(doc=b).id
        request.user = l
        approve_request(request)

        request.user = s3
        make_new(request)
        request.GET['user_id'] = s3.id
        request.GET['req_id'] = s3.request_set.get(doc=b).id
        request.user = l
        approve_request(request)

        self.assertEqual(len(b.documentcopy_set.all()), 2)
        self.assertEqual(len(s1.documentcopy_set.filter(doc=b)), 1)  # s1 has b
        self.assertEqual(len(s2.documentcopy_set.filter(doc=b)), 1)  # s2 has b
        self.assertEqual(len(s3.documentcopy_set.filter(doc=b)), 0)  # s3 has no b

    def test_TC6(self):
        p = User.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=p, status='student', phone_number=896000, address='2-107')
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',
                                             is_staff=True)

        b = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                edition=1, copies=2, authors='sadf', cover='cover', publisher='pub', is_bestseller=True)

        request = HttpRequest()
        request.GET['doc'] = b.id
        request.user = p
        make_new(request)  # request it out twice
        make_new(request)

        request.GET['user_id'] = p.id
        request.GET['req_id'] = p.request_set.get(doc=b).id
        request.user = librarian
        approve_request(request)

        self.assertEqual(len(b.documentcopy_set.all()), 1)

    def test_TC7(self):
        p1 = User.objects.create_user('s', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        p2 = User.objects.create_user('f', 'exampl2@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=p1, phone_number=123, status='student', address='1-103')
        UserProfile.objects.create(user=p2, phone_number=123, status='student', address='1-103')

        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',
                                             is_staff=True)
        UserProfile.objects.create(user=librarian, phone_number=123, status='faculty', address='1-103')

        b1 = Book.objects.create(title='b1', price=0, publication_date=datetime.datetime.now(),
                                 edition=1, copies=2, authors='sadf', cover='cover', publisher='pub')

        request = HttpRequest()
        request.GET['doc'] = b1.id
        request.user = p1
        make_new(request)

        request.user = librarian
        request.GET['user_id'] = p1.id
        request.GET['req_id'] = p1.request_set.get(doc=b1).id
        approve_request(request)

        request = HttpRequest()
        request.GET['doc'] = b1.id
        request.user = p2
        make_new(request)

        request.GET['user_id'] = p2.id
        request.GET['req_id'] = p2.request_set.get(doc=b1).id
        request.user = librarian
        approve_request(request)

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
        request.GET['doc'] = book.id
        request.user = student
        make_new(request)

        request.GET['user_id'] = student.id
        request.GET['req_id'] = student.request_set.get(doc=book).id
        request.user = librarian
        approve_request(request)

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
                                   edition=1, copies=1, authors='sadf', cover='cover', publisher='pub',
                                   is_bestseller=True)

        # 's' checks out book 'b'
        request = HttpRequest()
        request.GET['doc'] = book.id
        request.user = student
        make_new(request)

        request.GET['user_id'] = student.id
        request.GET['req_id'] = student.request_set.get(doc=book).id
        request.user = librarian
        approve_request(request)

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
        request.GET['doc'] = A.id
        request.user = student
        make_new(request)  # everything ok

        request.GET['user_id'] = student.id
        request.GET['req_id'] = student.request_set.get(doc=A).id
        request.user = librarian
        approve_request(request)

        request.GET['doc'] = B.id
        request.user = student
        make_new(request)  # request will not be created because of reference book
        try:
            request.GET['user_id'] = student.id
            request.GET['req_id'] = student.request_set.get(doc=A).id
        except:  # expected state: cant find such request and therefore cant approve
            pass
        else:
            raise Exception

        # The system allows to check out only the book A. The reference book B is not available for checking out
        number_copies_patron_has = len(student.documentcopy_set.all())
        self.assertEqual(number_copies_patron_has, 1)

        student.documentcopy_set.get(id=A.id)  # will raise error if copy of A doesn't exist


class Delivery2(TestCase):

    def test_TC1(self):

        """
        The system does not have any doc- uments, any pa- tron.
        The system only contains one user who is a li- brarian.
        """

        self.librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qerty', first_name='F', last_name='L',
                                                  is_staff=True)
        self.b1 = Book.objects.create(title='Introduction to Algorithms', price=0,
                                      publication_date=datetime.datetime.now(),
                                      edition=3, copies=3,
                                      authors='Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest and '
                                              'Clifford Stein', cover='cover', publisher='MIT Press')
        self.b2 = Book.objects.create(title='Design Patterns: Elements of Reusable Object-Oriented Software', price=0,
                                      publication_date=datetime.datetime.now(), edition=1, copies=2,
                                      authors='Erich Gamma, Ralph Johnson, John Vlissides, Richard Helm', cover='cover',
                                      publisher='Addison-Wesley Professional', is_bestseller=True)
        self.b3 = Book.objects.create(title='The Mythical Man-month', price=0, publication_date=datetime.datetime.now(),
                                      edition=2, copies=1,
                                      authors='Brooks,Jr., Frederick P.', cover='cover',
                                      publisher='Addison-Wesley Longman Publishing '
                                                'Co., Inc.', is_reference=True)

        self.av1 = AVFile.objects.create(title='Null References: The Billion Dollar Mistake', authors='Tony Hoare', type="AVFile", price=0)
        self.av2 = AVFile.objects.create(title=': Information Entropy', authors='Claude Shannon', price=0, type="AVFile")

        self.p1 = User.objects.create_user('patron1', 'exampl2@mail.ru', '12356qwerty', first_name='Sergey',
                                           last_name='Afonso')
        UserProfile.objects.create(user=self.p1, phone_number=30001, status='faculty', address='Via Margutta, 3')

        self.p2 = User.objects.create_user('patron2', 'exampl2@mail.ru', '12456qwerty', first_name='Nadia',
                                           last_name='Teixeira')
        UserProfile.objects.create(user=self.p2, phone_number=30002, status='student', address='Via Sacra, 13')

        self.p3 = User.objects.create_user('patron3', 'exampl2@mail.ru', '23456qwerty', first_name='Elvira',
                                           last_name='Espindola')
        UserProfile.objects.create(user=self.p3, phone_number=30003, status='student', address='Via del Corso, 22')

        num_of_docs = 0
        for doc in Document.objects.all():
            num_of_docs += doc.copies
        self.assertEqual(len(User.objects.all()), 4)
        self.assertEqual(num_of_docs, 8)

    def test_TC2(self):
        self.test_TC1()
        self.b1.copies -= 2
        self.b3.copies -= 1
        self.b1.save()
        self.b3.save()
        self.p2.delete()
        self.assertEqual(len(User.objects.all()), 3)
        num_of_docs = 0
        for doc in Document.objects.all():
            num_of_docs += doc.copies
        self.assertEqual(num_of_docs, 5)

    def test_TC3(self):
        self.test_TC1()
        request = HttpRequest()
        request.method = "GET"
        request.user = self.librarian

        request.GET['id'] = self.p1.id  # request information about p1
        response = user_card_info(request)
        self.assertTrue(
            all([word in response.content for word in [b'Sergey', b'Afonso', b'Via Margutta, 3', b'30001']]))

        request.GET['id'] = self.p3.id  # request information about p3
        response = user_card_info(request)
        self.assertTrue(
            all([word in response.content for word in [b'Elvira', b'Espindola', b'Via del Corso, 22', b'30003']]))

    def test_TC4(self):
        self.test_TC2()
        request = HttpRequest()
        request.method = "GET"
        request.user = self.librarian

        request.GET['id'] = self.p2.id
        response = user_card_info(request)
        self.assertEqual(str(response), 'No such user in library')  # not found such user

        request.GET['id'] = self.p3.id
        response = user_card_info(request)
        self.assertTrue(
            all([word in response.content for word in [b'Elvira', b'Espindola', b'Via del Corso, 22', b'30003']]))

    def test_TC5(self):
        value_error_has_raised = False

        self.test_TC2()

        request = HttpRequest()
        request.method = "GET"

        try:
            request.user = self.p2
            request.GET['doc'] = self.b1.id
            make_new(request)
        except ValueError:
            value_error_has_raised = True

        number_of_requests = Request.objects.all().count()

        self.assertEqual(value_error_has_raised, True)
        self.assertEqual(number_of_requests, 0)

    def test_TC6(self):
        self.test_TC2()

        # p1 leave a request for a book b1
        request = HttpRequest()
        request.method = "GET"
        request.user = self.p1
        request.GET['doc'] = self.b1.id
        make_new(request)

        # p3 leave a request for a book b1
        request.user = self.p3
        request.GET['doc'] = self.b1.id
        make_new(request)

        # p1 leave a request for a book b1
        request.user = self.p1
        request.GET['doc'] = self.b2.id
        make_new(request)

        # now librarian should approve requests
        request = HttpRequest()
        request.method = "GET"
        request.user = self.librarian

        # approve 1st
        request.GET['req_id'] = 1
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # approve 2nd
        request.GET['req_id'] = 2
        request.GET['user_id'] = self.p3.id
        approve_request(request)

        # approve 3rd
        request.GET['req_id'] = 3
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # check p1's info
        request.GET['id'] = self.p1.id
        response = user_card_info(request)

        self.assertTrue(
            all([word in response.content for word in
                 [b'Sergey', b'Afonso', b'Via Margutta, 3', b'30001', str(self.b1.title).encode(),
                  str(self.b2.title).encode()]]))

        # check p3's info
        request.GET['id'] = self.p3.id
        response = user_card_info(request)

        self.assertTrue(
            all([word in response.content for word in
                 [b'Elvira', b'Espindola', b'Via del Corso, 22', b'30003', ]]))

    def test_TC7(self):
        self.test_TC1()

        # Make requests for books by p1
        request = HttpRequest()
        request.GET['doc'] = self.b1.id
        request.user = self.p1
        make_new(request)

        request = HttpRequest()
        request.GET['doc'] = self.b2.id
        request.user = self.p1
        make_new(request)

        try:
            request = HttpRequest()
            request.GET['doc'] = self.b3.id
            request.user = self.p1
            make_new(request)
        except:
            pass

        request = HttpRequest()
        request.GET['doc'] = self.av1.id
        request.user = self.p1
        make_new(request)

        # Make requests for books by p2
        request = HttpRequest()
        request.GET['doc'] = self.b1.id
        request.user = self.p2
        make_new(request)

        request = HttpRequest()
        request.GET['doc'] = self.b2.id
        request.user = self.p2
        make_new(request)

        request = HttpRequest()
        request.GET['doc'] = self.av2.id
        request.user = self.p2
        make_new(request)

        # Accept all requests by labrarian
        request.GET['user_id'] = self.p1.id
        request.GET['req_id'] = self.p1.request_set.get(doc=self.b1).id
        request.user = self.librarian
        approve_request(request)

        request.GET['user_id'] = self.p1.id
        request.GET['req_id'] = self.p1.request_set.get(doc=self.b2).id
        request.user = self.librarian
        approve_request(request)

        try:
            request.GET['user_id'] = self.p1.id
            request.GET['req_id'] = self.p1.request_set.get(doc=self.b3).id
            request.user = self.librarian
            approve_request(request)
        except:
            pass

        request.GET['user_id'] = self.p1.id
        request.GET['req_id'] = self.p1.request_set.get(doc=self.av1).id
        request.user = self.librarian
        approve_request(request)

        request.GET['user_id'] = self.p2.id
        request.GET['req_id'] = self.p2.request_set.get(doc=self.b1).id
        request.user = self.librarian
        approve_request(request)

        request.GET['user_id'] = self.p2.id
        request.GET['req_id'] = self.p2.request_set.get(doc=self.b2).id
        request.user = self.librarian
        approve_request(request)

        request.GET['user_id'] = self.p2.id
        request.GET['req_id'] = self.p2.request_set.get(doc=self.av2).id
        request.user = self.librarian
        approve_request(request)

        # Make request to get info about user
        request = HttpRequest()
        request.method = "GET"
        request.user = self.librarian

        request.GET['id'] = self.p1.id  # request information about p1
        response = user_card_info(request)

        self.assertTrue(
            all([word in response.content for word in [b'Sergey', b'Afonso', b'Via Margutta, 3', b'30001']]))

        returning_date = self.p1.documentcopy_set.get(doc=self.b1).returning_date
        should_be_today = returning_date - datetime.timedelta(days=27)
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertTrue(should_be_today)

        returning_date = self.p1.documentcopy_set.get(doc=self.b2).returning_date
        should_be_today = returning_date - datetime.timedelta(days=27)
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertTrue(should_be_today)

        returning_date = self.p1.documentcopy_set.get(doc=self.av1).returning_date
        should_be_today = returning_date - datetime.timedelta(days=14)
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertTrue(should_be_today)

        returning_date = self.p2.documentcopy_set.get(doc=self.b1).returning_date
        should_be_today = returning_date - datetime.timedelta(days=21)
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertTrue(should_be_today)

        returning_date = self.p2.documentcopy_set.get(doc=self.b2).returning_date
        should_be_today = returning_date - datetime.timedelta(days=21)
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertTrue(should_be_today)

        returning_date = self.p2.documentcopy_set.get(doc=self.av2).returning_date
        should_be_today = returning_date - datetime.timedelta(days=14)
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertTrue(should_be_today)

        request.GET['id'] = self.p1.id  # request information about p3
        response = user_card_info(request)
        self.assertTrue(
            all([word in response.content for word in [b'Sergey', b'Afonso', b'Via Margutta, 3', b'30001',
                                                       str(self.b1.title).encode(), str(self.b2.title).encode(),
                                                       str(self.av1.title).encode()]]
                ))

        request.GET['id'] = self.p2.id  # request information about p3
        response = user_card_info(request)
        self.assertTrue(
            all([word in response.content for word in [b'Nadia', b'Teixeira', b'Via Sacra, 13', b'30002',
                                                       str(self.b1.title).encode(),
                                                       str(self.b2.title).encode(),
                                                       str(self.av2.title).encode()]]))

    def test_TC8(self):
        """
        p1 checked-out b1 on February 9th and b2 on February 2nd
        p2 checked-out b1 on February 5th and av1 on February 17th
        """
        self.test_TC1()

        request = HttpRequest()
        request.GET['doc'] = self.b1.id
        request.user = self.p1
        make_new(request)

        request = HttpRequest()
        request.GET['doc'] = self.b2.id
        request.user = self.p1
        make_new(request)

        request.GET['user_id'] = self.p1.id
        request.GET['req_id'] = self.p1.request_set.get(doc=self.b1).id
        request.user = self.librarian
        approve_request(request)

        request.GET['user_id'] = self.p1.id
        request.GET['req_id'] = self.p1.request_set.get(doc=self.b2).id
        request.user = self.librarian
        approve_request(request)

        request = HttpRequest()
        request.GET['doc'] = self.b1.id
        request.user = self.p2
        make_new(request)

        request = HttpRequest()
        request.GET['doc'] = self.av1.id
        request.user = self.p2
        make_new(request)

        request.GET['user_id'] = self.p2.id
        request.GET['req_id'] = self.p2.request_set.get(doc=self.b1).id
        request.user = self.librarian
        approve_request(request)

        request.GET['user_id'] = self.p2.id
        request.GET['req_id'] = self.p2.request_set.get(doc=self.av1).id
        request.user = self.librarian
        approve_request(request)

        p1_b1 = self.p1.documentcopy_set.filter(doc=self.b1)[0]

        p1_b1.returning_date = (datetime.datetime.strptime("2018-02-09 00:00",
                                                           '%Y-%m-%d %H:%M') + datetime.timedelta(days=21)).strftime(
            "%Y-%m-%d %H:%M")
        p1_b1.date = datetime.datetime.strptime("2018-02-09 00:00",
                                                "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")
        p1_b1.save()

        p1_b2 = self.p1.documentcopy_set.filter(doc=self.b2)[0]
        p1_b2.returning_date = (datetime.datetime.strptime("2018-02-02 00:00",
                                                           '%Y-%m-%d %H:%M') + datetime.timedelta(days=21)).strftime(
            "%Y-%m-%d %H:%M")
        p1_b2.date = datetime.datetime.strptime("2018-02-02 00:00",
                                                "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")
        p1_b2.save()

        p2_b1 = self.p2.documentcopy_set.filter(doc=self.b1)[0]
        p2_b1.returning_date = (datetime.datetime.strptime("2018-02-05 00:00",
                                                           '%Y-%m-%d %H:%M') + datetime.timedelta(days=21)).strftime(
            "%Y-%m-%d %H:%M")
        p2_b1.date = datetime.datetime.strptime("2018-02-05 00:00",
                                                "%Y-%m-%d %H:%M")
        p2_b1.save()

        p2_av1 = self.p2.documentcopy_set.filter(doc=self.av1)[0]
        p2_av1.returning_date = (datetime.datetime.strptime("2018-02-17 00:00",
                                                            '%Y-%m-%d %H:%M') + datetime.timedelta(days=14)).strftime(
            "%Y-%m-%d %H:%M")
        p2_av1.date = datetime.datetime.strptime("2018-02-17 00:00",
                                                 "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")
        p2_av1.save()

        now_aware = timezone.now()

        p1_have_overdue_on_b2_in_3_days = (datetime.datetime.strptime("2018-03-05 00:00", "%Y-%m-%d  %H:%M") -
                                           datetime.datetime.strptime(p1_b1.returning_date,
                                                                      "%Y-%m-%d  %H:%M")).days == 3
        p2_have_overdue_on_b1_in_7_days = (datetime.datetime.strptime("2018-03-05 00:00", "%Y-%m-%d  %H:%M") -
                                           datetime.datetime.strptime(p2_b1.returning_date,
                                                                      "%Y-%m-%d  %H:%M")).days == 7
        p2_have_overdue_on_av1_in_2_days = (datetime.datetime.strptime("2018-03-05 00:00", "%Y-%m-%d  %H:%M") -
                                            datetime.datetime.strptime(p2_av1.returning_date,
                                                                       "%Y-%m-%d  %H:%M")).days == 2

        self.assertEqual(p1_have_overdue_on_b2_in_3_days, True)
        self.assertEqual(p2_have_overdue_on_av1_in_2_days, True)
        self.assertEqual(p2_have_overdue_on_b1_in_7_days, True)

