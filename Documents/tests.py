from django.core import mail
from django.test import TestCase, Client, RequestFactory

from BookRequests.models import Request
from Documents.librarian_view import update_doc, get_doc, get_fields_of
from UserCards.models import UserProfile
from django.http import HttpRequest, Http404, QueryDict
from .models import *
from BookRequests.views import *
import BookRequests
from Documents.views import get_logging
import datetime
from UserCards.forms import AdminCreateUserForm
from UserCards.views import user_card_info, CreateUserView
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
        UserProfile.objects.create(user=librarian, phone_number=123, status='professor', address='1-103')

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
        professor = User.objects.create_user('f', 'exampl2@mail.ru', '123456qwerty', first_name='F', last_name='L')
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',
                                             is_staff=True)
        UserProfile.objects.create(user=student, phone_number=123, status='student', address='1-103')
        UserProfile.objects.create(user=professor, phone_number=123, status='professor', address='1-103')
        UserProfile.objects.create(user=librarian, phone_number=123, status='professor', address='1-103')
        # book
        book = Book.objects.create(title='title', price=0, publication_date=datetime.datetime.now(),
                                   edition=1, copies=2, authors='sadf', cover='cover', publisher='pub')

        # professor checks out book
        request = HttpRequest()
        request.GET['doc'] = book.id
        request.user = professor
        make_new(request)

        request.GET['user_id'] = professor.id
        request.GET['req_id'] = professor.request_set.get(doc=book).id
        request.user = librarian
        approve_request(request)

        # professor has 4 weeks to return this book since today
        returning_date = professor.documentcopy_set.get(doc=book).returning_date
        should_be_today = returning_date - datetime.timedelta(days=28)  # 4 weeks = 28 days
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)

        self.assertEqual(should_be_today, datetime.date.today())

    def test_TC4(self):
        #
        f = User.objects.create_user('professor', 'fac@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=f, status='professor', phone_number=896000, address='2-107')

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
        UserProfile.objects.create(user=librarian, phone_number=123, status='professor', address='1-103')

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
        professor = User.objects.create_user('f', 'exampl2@mail.ru', '123456qwerty', first_name='F', last_name='L')
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',
                                             is_staff=True)

        UserProfile.objects.create(user=student, phone_number=123, status='student', address='1-103')
        UserProfile.objects.create(user=professor, phone_number=123, status='professor', address='1-103')
        UserProfile.objects.create(user=librarian, phone_number=123, status='professor', address='1-103')

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

        # The library has at least one patron (professor) 'f' and one patron (Student) 's', and a librarian. It also has book 'b'
        # that is best seller
        student = User.objects.create_user('s', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=student, phone_number=123, status='student', address='1-103')
        professor = User.objects.create_user('f', 'exampl2@mail.ru', '123456qwerty', first_name='F', last_name='L')
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

        self.av1 = AVFile.objects.create(title='Null References: The Billion Dollar Mistake', authors='Tony Hoare',
                                         type="AVFile", price=0)
        self.av2 = AVFile.objects.create(title=': Information Entropy', authors='Claude Shannon', price=0,
                                         type="AVFile")

        self.p1 = User.objects.create_user('patron1', 'exampl2@mail.ru', '12356qwerty', first_name='Sergey',
                                           last_name='Afonso')
        UserProfile.objects.create(user=self.p1, phone_number=30001, status='professor', address='Via Margutta, 3')

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

        # p1 leaves a request for a book b1
        request = HttpRequest()
        request.method = "GET"
        request.user = self.p1
        request.GET['doc'] = self.b1.id
        make_new(request)

        # p3 leaves a request for a book b1
        request.user = self.p3
        request.GET['doc'] = self.b1.id
        make_new(request)

        # p1 leaves a request for a book b2
        request.user = self.p1
        request.GET['doc'] = self.b2.id
        make_new(request)

        # now librarian should approve requests
        request = HttpRequest()
        request.method = "GET"
        request.user = self.librarian

        # approve 1st
        request.GET['req_id'] = self.p1.request_set.get(doc=self.b1).id
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # approve 2nd
        request.GET['req_id'] = self.p3.request_set.get(doc=self.b1).id
        request.GET['user_id'] = self.p3.id
        approve_request(request)

        # approve 3rd
        request.GET['req_id'] = self.p1.request_set.get(doc=self.b2).id
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # check p1's info
        request.GET['id'] = self.p1.id
        response = user_card_info(request)

        self.assertTrue(
            all([word in response.content for word in
                 [b'Sergey', b'Afonso', b'Via Margutta, 3', b'30001', str(self.b1.title).encode(), b'27days']]))

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


class Delivery3(TestCase):

    def test_init_db(self):
        self.d1 = Book.objects.create(title='Introduction to Algorithms', price=5000,
                                      publication_date=datetime.date(year=2009, month=1, day=1),
                                      edition=3, copies=3,
                                      authors='Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest and '
                                              'Clifford Stein', cover='cover', publisher='MIT Press')
        self.d2 = Book.objects.create(title='Design Patterns: Elements of Reusable Object-Oriented Software',
                                      price=1700,
                                      publication_date=datetime.date(year=2003, month=1, day=1),
                                      edition=1, copies=3, is_bestseller=True,
                                      authors='Erich Gamma, Ralph Johnson, John Vlissides, Richard Helm',
                                      cover='cover', publisher='Addison-Wesley Professional')
        self.d3 = Book.objects.create(title='Null References: The Billion Dollar Mistake', price=700,
                                      publication_date=datetime.date(year=2003, month=1, day=1),
                                      edition=1, copies=2,
                                      authors='Tony Hoare',
                                      cover='cover', publisher='lalalend')

        self.librarian = User.objects.create_user('librarian2', 'exampl23@mail.ru', '123456qerty', first_name='F',
                                                  last_name='L',
                                                  is_staff=True)

        self.p1 = User.objects.create_user('patron1', 'p1@mail.ru', '12356qwerty', first_name='Sergey',
                                           last_name='Afonso')
        UserProfile.objects.create(user=self.p1, phone_number=30001, status='professor', address='Via Margutta, 3')

        self.p2 = User.objects.create_user('patron2', 'p2@mail.ru', '12456qwerty', first_name='Nadia',
                                           last_name='Teixeira')
        UserProfile.objects.create(user=self.p2, phone_number=30002, status='professor', address='Via Sacra, 13')

        self.p3 = User.objects.create_user('patron3', 'p3@mail.ru', '23456qwerty', first_name='Elvira',
                                           last_name='Espindola')
        UserProfile.objects.create(user=self.p3, phone_number=30003, status='professor', address='Via del Corso, 22')

        self.s = User.objects.create_user('patron4', 's@mail.ru', '23456qwerty', first_name='Andrey',
                                          last_name='Velo')
        UserProfile.objects.create(user=self.s, phone_number=30004, status='student', address='Avenida Mazatlan 250')

        self.v = User.objects.create_user('patron5', 'v@mail.ru', '23456qwerty', first_name='Veronika',
                                          last_name='Rama')
        UserProfile.objects.create(user=self.v, phone_number=30005, status='visiting professor',
                                   address='Stret Atocha, 27')

    def test_TC1(self):
        self.test_init_db()
        request = HttpRequest()
        request.method = "GET"
        request.user = self.p1
        # p1 leaves a request for a book d1
        request.GET['doc'] = self.d1.id
        make_new(request)
        # p1 leaves a request for a book d2
        request.GET['doc'] = self.d2.id
        make_new(request)

        # now librarian should approve requests
        request = HttpRequest()
        request.user = self.librarian

        # approve 1st
        request.GET['req_id'] = self.p1.request_set.get(doc=self.d1).id
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # approve 2st
        request.GET['req_id'] = self.p1.request_set.get(doc=self.d2).id
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # requests made in march 5th and action happens in 2nd april (i.e. today is returning day)
        p1_d1_copy = self.p1.documentcopy_set.get(id=self.d1.id)
        p1_d1_copy.returning_date = datetime.datetime.now()
        p1_d2_copy = self.p1.documentcopy_set.get(id=self.d2.id)
        p1_d2_copy.returning_date = datetime.datetime.now()

        # p1 returns d2
        request.GET['copy_id'] = self.p1.documentcopy_set.get(id=self.d2.id).id
        return_doc(request)

        # librarian checks dues and fines of p1
        request.GET['id'] = self.p1.id
        response = user_card_info(request)
        f = p1_d1_copy.fine()  # fine of d1
        self.assertEqual(f, 0)
        self.assertTrue(str(f).encode() in response.content)

    def test_TC2(self):
        self.test_init_db()
        request = HttpRequest()
        request.method = "GET"
        request.user = self.p1

        # p1 leaves a request for a book d1
        request.GET['doc'] = self.d1.id
        make_new(request)
        # p1 leaves a request for a book d2
        request.GET['doc'] = self.d2.id
        make_new(request)

        # now librarian should approve requests
        request.user = self.librarian

        # approve 1st
        request.GET['req_id'] = self.p1.request_set.get(doc=self.d1).id
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # approve 2st
        request.GET['req_id'] = self.p1.request_set.get(doc=self.d2).id
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # requests made in march 5th and action happens in 2nd april (i.e. today is returning day)
        p1_d1_copy = self.p1.documentcopy_set.get(id=self.d1.id)
        p1_d1_copy.returning_date = datetime.datetime.now()
        p1_d2_copy = self.p1.documentcopy_set.get(id=self.d2.id)
        p1_d2_copy.returning_date = datetime.datetime.now()

        request.user = self.s
        # s leaves a request for a book d1
        request.GET['doc'] = self.d1.id
        make_new(request)

        # s leaves a request for a book d2
        request.GET['doc'] = self.d2.id
        make_new(request)

        # now librarian should approve requests
        request.user = self.librarian

        # approve 1st
        request.GET['req_id'] = self.s.request_set.get(doc=self.d1).id
        request.GET['user_id'] = self.s.id
        approve_request(request)

        # approve 2st
        request.GET['req_id'] = self.s.request_set.get(doc=self.d2).id
        request.GET['user_id'] = self.s.id
        approve_request(request)

        # requests made in march 5th and action happens in 2nd april (i.e. today is returning day)
        s_d1_copy = self.s.documentcopy_set.get(doc=self.d1)
        s_d1_copy.returning_date = datetime.datetime.now() - datetime.timedelta(days=7)
        s_d2_copy = self.s.documentcopy_set.get(doc=self.d2)
        s_d2_copy.returning_date = datetime.datetime.now() - datetime.timedelta(days=14)

        request.user = self.v
        # v leaves a request for a book d1
        request.GET['doc'] = self.d1.id
        make_new(request)

        # v leaves a request for a book d2
        request.GET['doc'] = self.d2.id
        make_new(request)

        # now librarian should approve requests
        request.user = self.librarian

        # approve 1st
        request.GET['req_id'] = self.v.request_set.get(doc=self.d1).id
        request.GET['user_id'] = self.v.id
        approve_request(request)

        # approve 2st
        request.GET['req_id'] = self.v.request_set.get(doc=self.d2).id
        request.GET['user_id'] = self.v.id
        approve_request(request)

        # requests made in march 5th and action happens in 2nd april (i.e. today is returning day)
        v_d1_copy = self.s.documentcopy_set.get(doc=self.d1)
        v_d1_copy.returning_date = datetime.datetime.now() - datetime.timedelta(days=21)
        v_d2_copy = self.s.documentcopy_set.get(doc=self.d2)
        v_d2_copy.returning_date = datetime.datetime.now() - datetime.timedelta(days=21)

        # librarian checks dues and fines of p1
        request.GET['id'] = self.p1.id
        response = user_card_info(request)
        f1 = p1_d1_copy.fine()  # fine of d1
        f2 = p1_d2_copy.fine()  # fine of d2
        self.assertEqual(f1, 0)
        self.assertEqual(f2, 0)

        # librarian checks dues and fines of s
        request.GET['id'] = self.s.id
        response = user_card_info(request)
        f1 = s_d1_copy.fine()  # fine of d1
        f2 = s_d2_copy.fine()  # fine of d2
        self.assertEqual(f1, 700)
        self.assertEqual(f2, 1400)

        # librarian checks dues and fines of v
        request.GET['id'] = self.v.id
        response = user_card_info(request)
        f1 = v_d1_copy.fine()  # fine of d1
        f2 = v_d2_copy.fine()  # fine of d2
        self.assertEqual(f1, 2100)
        self.assertEqual(f2, 1700)

    def test_TC3(self):
        self.test_init_db()
        request = HttpRequest()
        request.method = "GET"
        request.user = self.p1

        # p1 leaves a request for a book d1
        request.GET['doc'] = self.d1.id
        make_new(request)

        # s leaves a request for a book d2
        request.user = self.s
        request.GET['doc'] = self.d2.id
        make_new(request)

        # v leaves a request for a book d2
        request.user = self.v
        request.GET['doc'] = self.d2.id
        make_new(request)

        request.user = self.librarian
        # approve 1st
        request.GET['req_id'] = self.p1.request_set.get(doc=self.d1).id
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # approve 2nd
        request.GET['req_id'] = self.s.request_set.get(doc=self.d2).id
        request.GET['user_id'] = self.s.id
        approve_request(request)

        # approve 3rd
        request.GET['req_id'] = self.v.request_set.get(doc=self.d2).id
        request.GET['user_id'] = self.v.id
        approve_request(request)

        # p1 renews d1
        request.user = self.p1
        request.GET['copy_id'] = self.p1.documentcopy_set.get(doc=self.d1).id
        renew(request)

        # s renews d2
        request.user = self.s
        request.GET['copy_id'] = self.s.documentcopy_set.get(doc=self.d2).id
        renew(request)

        # v renews d2
        request.user = self.v
        request.GET['copy_id'] = self.v.documentcopy_set.get(doc=self.d2).id
        renew(request)

        # librarian checks the information of p1
        should_be_today = self.p1.documentcopy_set.get(doc=self.d1).returning_date - datetime.timedelta(
            days=28)  # he renewed d1, so 28 days left
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertEqual(should_be_today, datetime.date.today())

        # librarian checks the information of s
        should_be_today = self.s.documentcopy_set.get(doc=self.d2).returning_date - datetime.timedelta(
            days=14)  # he renewed d1, so 14 days left
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertEqual(should_be_today, datetime.date.today())

        # librarian checks the information of v
        should_be_today = self.v.documentcopy_set.get(doc=self.d2).returning_date - datetime.timedelta(
            days=7)  # he renewed d1, so 7 days left
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertEqual(should_be_today, datetime.date.today())

    def test_TC4(self):
        self.test_init_db()
        request = HttpRequest()
        request.method = "GET"
        request.user = self.p1
        # p1 leaves a request for a book d1
        request.GET['doc'] = self.d1.id
        make_new(request)
        # s leaves a request for a book d2
        request.user = self.s
        request.GET['doc'] = self.d2.id
        make_new(request)
        # v leaves a request for a book d2
        request.user = self.v
        request.GET['doc'] = self.d2.id
        make_new(request)

        request.user = self.librarian
        # approve 1st
        request.GET['req_id'] = self.p1.request_set.get(doc=self.d1).id
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # approve 2nd
        request.GET['req_id'] = self.s.request_set.get(doc=self.d2).id
        request.GET['user_id'] = self.s.id
        approve_request(request)

        # approve 3rd
        request.GET['req_id'] = self.v.request_set.get(doc=self.d2).id
        request.GET['user_id'] = self.v.id
        approve_request(request)

        # outstanding request for d2
        request.GET['doc_id'] = self.d2.id
        outstanding_request(request)

        # p1 renews d1
        request.user = self.p1
        request.GET['copy_id'] = self.p1.documentcopy_set.get(doc=self.d1).id
        renew(request)
        # s renews d2
        request.user = self.s
        request.GET['copy_id'] = self.s.documentcopy_set.get(doc=self.d2).id
        renew(request)
        # v renews d2
        request.user = self.v
        request.GET['copy_id'] = self.v.documentcopy_set.get(doc=self.d2).id
        renew(request)

        # returning date of d1 for p1 is (date_when_was_made_checkout - 28_days)
        should_be_today = self.p1.documentcopy_set.get(doc=self.d1).returning_date - datetime.timedelta(days=28)
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertEqual(should_be_today, datetime.date.today())
        #
        should_be_today = self.s.documentcopy_set.get(doc=self.d2).returning_date - datetime.timedelta(days=14)
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertEqual(should_be_today, datetime.date.today())
        #
        should_be_today = self.v.documentcopy_set.get(doc=self.d2).returning_date - datetime.timedelta(days=7)
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)
        self.assertEqual(should_be_today, datetime.date.today())

    def test_TC5(self):
        self.test_init_db()
        # p1 leaves a request for a book d3
        request = HttpRequest()
        request.method = "GET"
        request.user = self.p1
        request.GET['doc'] = self.d3.id
        make_new(request)

        # s leaves a request for a book d3
        request.user = self.s
        request.GET['doc'] = self.d3.id
        make_new(request)

        # v leaves a request for a book d3
        request.user = self.v
        request.GET['doc'] = self.d3.id
        make_new(request)

        # now librarian should approve requests
        request = HttpRequest()
        request.method = "GET"
        request.user = self.librarian

        # approve 1st (p1 d3)
        request.GET['req_id'] = self.p1.request_set.get(doc=self.d3).id
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # approve 2nd (s d3)
        request.GET['req_id'] = self.s.request_set.get(doc=self.d3).id
        request.GET['user_id'] = self.s.id
        approve_request(request)

        # librarian cannot approve third request because there is no button
        # "approve" for him (since there is no copy available)

        # librarian checks the waiting list for the document d3
        request.GET['id'] = self.d3.id
        # get response and render response
        response = RequestsView.as_view()(request)
        response = response.render()

        # check if librarian will see the name of user v (patron5) in waiting list
        self.assertTrue(
            all([word in response.content for word in
                 [b'patron5']]))

    def test_TC6(self):
        self.test_init_db()
        # p1 leaves a request for a book d3
        request = HttpRequest()
        request.method = "GET"
        request.user = self.p1
        request.GET['doc'] = self.d3.id
        make_new(request)

        # p2 leaves a request for a book d3
        request.user = self.p2
        request.GET['doc'] = self.d3.id
        make_new(request)

        # s leaves a request for a book d3
        request.user = self.s
        request.GET['doc'] = self.d3.id
        make_new(request)

        # v leaves a request for a book d3
        request.user = self.v
        request.GET['doc'] = self.d3.id
        make_new(request)

        # p3 leaves a request for a book d3
        request.user = self.p3
        request.GET['doc'] = self.d3.id
        make_new(request)

        # now librarian should approve requests
        request = HttpRequest()
        request.method = "GET"
        request.user = self.librarian

        # approve 1st (p1 d3)
        request.GET['req_id'] = self.p1.request_set.get(doc=self.d3).id
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # approve 2nd (p2 d3)
        request.GET['req_id'] = self.p2.request_set.get(doc=self.d3).id
        request.GET['user_id'] = self.p2.id
        approve_request(request)

        # librarian cannot approve three last requests because there is no button
        # "approve" for him (since there are no copies available)

        # librarian checks the waiting list for the document d3
        request.GET['id'] = self.d3.id
        response = RequestsView.as_view()(request)
        response = response.render()

        self.assertTrue(
            all([word in response.content for word in
                 [b'patron5', b'patron4', b'patron3']]))

        def test_TC7(self):
            self.test_TC6()

    def test_TC7(self):
        self.test_TC6()

        # librarian place an outstanding request on document d3
        request = HttpRequest()
        request.method = "GET"
        request.user = self.librarian
        request.GET['doc_id'] = self.d3.id
        outstanding_request(request)

        response = RequestsView.as_view()(request)
        response = response.render()

        self.assertTrue(not all([word in response.content for word in
                                 [b'patron5', b'patron4', b'patron3']]))

        # 12 because:
        # 5 for coming to library for doc approving to p1, p2, p3, s, v
        # 2 to p1 and p2 about approved request,
        # 3 to s, v, p3 for d3 not longer available
        # 2 to p1 and p2 to return books,

        self.assertEqual(len(mail.outbox), 12)

        for i in range(0, 4):
            self.assertEqual(mail.outbox[i].subject, 'Come to library for document approving')

        self.assertEqual(mail.outbox[5].to, ['p1@mail.ru'])
        self.assertEqual(mail.outbox[6].to, ['p2@mail.ru'])
        self.assertEqual(mail.outbox[5].subject, 'Approved request')
        self.assertEqual(mail.outbox[6].subject, 'Approved request')

        self.assertEqual(mail.outbox[7].to, ['p3@mail.ru'])
        self.assertEqual(mail.outbox[8].to, ['s@mail.ru'])
        self.assertEqual(mail.outbox[9].to, ['v@mail.ru'])

        self.assertEqual(mail.outbox[10].to, ['p1@mail.ru'])
        self.assertEqual(mail.outbox[11].to, ['p2@mail.ru'])

        for i in range(7, 11):
            self.assertEqual(mail.outbox[i].subject, 'Outstanding request')

    def test_TC8(self):
        self.test_TC6()
        request = HttpRequest()
        request.method = 'GET'
        request.user = self.librarian
        request.GET['copy_id'] = self.p2.documentcopy_set.get(doc=self.d3).id
        request.GET['debug'] = True

        self.s.email = 'name_that_hopely_no_one_in_the_world_will_choose@email.ru'
        self.s.save()

        return_doc(request)

        # check that mail had sent
        # on each email sending django.core.mail check that it was successfully sent to the user
        # if flag 'fail_silently' equal to False.

        # check that p2 have no any document
        self.assertEqual(len(self.p2.documentcopy_set.all()), 0)

        # librarian checks the waiting list for the document d3
        request.GET['id'] = self.d3.id
        response = RequestsView.as_view()(request)
        response = response.render()

        self.assertTrue(
            all([word in response.content for word in
                 [b'patron5', b'patron4', b'patron3']]))

    def test_TC9(self):
        self.test_TC6()
        request = HttpRequest()
        request.user = self.p1
        request.method = 'GET'
        request.GET['copy_id'] = self.p1.documentcopy_set.get(doc=self.d3).id
        renew(request)

        copy = self.p1.documentcopy_set.get(doc=self.d3)
        self.assertEqual((copy.returning_date - copy.date).days, 27)

        # librarian checks the waiting list for the document d3
        request.user = self.librarian
        request.GET['id'] = self.d3.id
        response = RequestsView.as_view()(request)
        response = response.render()

        self.assertTrue(
            all([word in response.content for word in
                 [b'patron5', b'patron4', b'patron3']]))

    def test_TC10(self):
        self.test_init_db()

        request = HttpRequest()
        request.method = "GET"
        request.user = self.p1

        # p1 leaves a request for a book d1
        request.GET['doc'] = self.d1.id
        make_new(request)

        # v leaves a request for a book d1
        request.user = self.v
        request.GET['doc'] = self.d1.id
        make_new(request)

        request.user = self.librarian
        # approve 1st
        request.GET['req_id'] = self.p1.request_set.get(doc=self.d1).id
        request.GET['user_id'] = self.p1.id
        approve_request(request)

        # approve 2nd
        request.GET['req_id'] = self.v.request_set.get(doc=self.d1).id
        request.GET['user_id'] = self.v.id
        approve_request(request)

        # change date on book copies
        delta = abs((self.p1.documentcopy_set.get(doc=self.d1).date -
                     datetime.datetime.strptime('2018-03-26 00:00', '%Y-%m-%d %H:%M')).days)

        doc = self.p1.documentcopy_set.get(doc=self.d1)
        doc.returning_date = (doc.returning_date - datetime.timedelta(days=delta)).strftime('%Y-%m-%d %H:%M')
        doc.date = "2018-03-26"
        doc.save()

        doc = self.v.documentcopy_set.get(doc=self.d1)
        doc.returning_date = (doc.returning_date -
                              datetime.timedelta(days=delta)).strftime('%Y-%m-%d %H:%M')
        doc.date = "2018-03-26"
        doc.save()

        # p1 renews d1
        request.user = self.p1
        request.GET['copy_id'] = self.p1.documentcopy_set.get(doc=self.d1).id
        renew(request)

        # v renews d1
        request.user = self.v
        request.GET['copy_id'] = self.v.documentcopy_set.get(doc=self.d1).id
        renew(request)

        should_be_today_p1 = self.p1.documentcopy_set.get(doc=self.d1).returning_date == '2018-04-26 00:00'
        should_be_today_v = self.v.documentcopy_set.get(doc=self.d1).returning_date == '2018-04-05 00:00'
        self.assertEqual(should_be_today_p1, should_be_today_v)


class Delivery4(TestCase):

    def test_init_db(self):
        self.admin = User.objects.create('admin1', 'ad@mail.ru', '12356qwerty',
                                           first_name='admin',
                                           last_name='admin', is_superuser=True)

        UserProfile.objects.create(user=self.admin,
                                   phone_number=30001,
                                   status='admin',
                                   address='Via Margutta, 3')

        self.d1 = Book.objects.create(title='Introduction to Algorithms',
                                      price=5000,
                                      publication_date=datetime.date(year=2009, month=1, day=1),
                                      edition=3,
                                      copies=0,
                                      authors='Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest and Clifford '
                                              'Stein',
                                      cover='cover',
                                      publisher='MIT Press',
                                      keywords='Algorithms, Data Structures, Complexity, Computational Theory')

        self.d2 = Book.objects.create(title='Algorithms + Data Structures = Programs',
                                      price=5000,
                                      publication_date=datetime.date(year=1978, month=1, day=1),
                                      edition=1,
                                      copies=0,
                                      is_bestseller=True,
                                      authors='Niklaus Wirth',
                                      cover='cover',
                                      publisher='Prentice Hall PTR',
                                      keywords='Algorithms, Data Structures, Search Algorithms, Pascal')
        self.d3 = Book.objects.create(title='The Art of Computer Programming',
                                      price=5000,
                                      publication_date=datetime.date(year=1997, month=1, day=1),
                                      edition=3,
                                      copies=0,
                                      authors='Donald E. Knuth',
                                      cover='cover',
                                      publisher='Addison Wesley Longman Publishing Co., Inc.',
                                      keywords='Algorithms, Combinatorial Algorithms, Recursion')


    def test_TC2(self):

        self.l1 = User.objects.create_user('librarian1', 'exampl2@mail.ru', '12356qwerty',
                                           first_name='Librarian',
                                           last_name='One',
                                           is_staff=True)
        UserProfile.objects.create(user=self.l1,
                                   phone_number=10001,
                                   status='librarian',
                                   address='Innopolis',
                                   privileges='priv1')

        self.l2 = User.objects.create_user('librarian2', 'exampl2@mail.ru', '12356qwerty', first_name='Librarian',
                                           last_name='Two',
                                           is_staff=True)
        UserProfile.objects.create(user=self.l2,
                                   phone_number=10002,
                                   status='librarian',
                                   address='Innopolis',
                                   privileges='priv2')

        self.l3 = User.objects.create_user('librarian3', 'exampl2@mail.ru', '12356qwerty', first_name='Librarian',
                                           last_name='Three',
                                           is_staff=True)
        UserProfile.objects.create(user=self.l3,
                                   phone_number=10003,
                                   status='librarian',
                                   address='Innopolis',
                                   privileges='priv3')

        self.assertEqual(len(UserProfile.objects.filter(status='librarian')), 3)

    def test_TC3(self):

        self.test_init_db()
        self.test_TC2()



    def test_TC4(self):

        self.test_init_db()

        def setup_view(view, request, *args, **kwargs):
            view.request = request
            view.args = args
            view.kwargs = kwargs
            return view

        self.test_TC2()

        # #all requered copies created by l2
        request = HttpRequest()
        request.method = "GET"
        request.user = self.l2

        # for d1
        doc = get_doc(request, self.d1.id)

        fields = get_fields_of(doc)
        fields = dict(fields)

        fields['copies'] = '3'
        fields['submit'] = 'Submit'

        qdict = QueryDict('', mutable=True)
        qdict.update(fields)

        request.method = "POST"
        request.POST = qdict
        update_doc(request, self.d1.id)

        # for d2
        doc = get_doc(request, self.d2.id)

        fields = get_fields_of(doc)
        fields = dict(fields)

        fields['copies'] = '3'
        fields['submit'] = 'Submit'

        qdict = QueryDict('', mutable=True)
        qdict.update(fields)

        request.method = "POST"
        request.POST = qdict
        update_doc(request, self.d2.id)

        # for d3
        doc = get_doc(request, self.d3.id)

        fields = get_fields_of(doc)
        fields = dict(fields)

        fields['copies'] = '3'
        fields['submit'] = 'Submit'

        qdict = QueryDict('', mutable=True)
        qdict.update(fields)

        request.method = "POST"
        request.POST = qdict
        update_doc(request, self.d3.id)

        self.assertEqual(Document.objects.get(id=self.d1.id).copies, 3)
        self.assertEqual(Document.objects.get(id=self.d2.id).copies, 3)
        self.assertEqual(Document.objects.get(id=self.d3.id).copies, 3)

        # Creating requestFactory for work with creation user forms
        factory = RequestFactory()
        request = factory.post('/user/create_user')
        request.user = self.l2

        # now l2 will create users using forms

        # create s1
        form_data_s = {'username': 'patron4',
                       'status': "student",
                       'privileges': "no privileges",
                       'email': 's@mail.ru',
                       'address': 'Avenida Mazatlan 250',
                       'phone_number': '30004',
                       'first_name': 'Andrey',
                       'last_name': 'Velo',
                       'password1': '23456qwerty',
                       'password2': '23456qwerty',
                       'submit': 'Submit'
                       }

        request.POST = form_data_s
        v = setup_view(CreateUserView, request)
        v.post(v, request)

        # create p1
        form_data_p1 = {'username': 'patron1',
                        'status': "professor",
                        'privileges': "no privileges",
                        'email': 'p1@mail.ru',
                        'address': 'Via Margutta, 3',
                        'phone_number': '30001',
                        'first_name': 'Sergey',
                        'last_name': 'Afonso',
                        'password1': '12356qwerty',
                        'password2': '12356qwerty',
                        'submit': 'Submit'
                        }

        request.POST = form_data_p1
        v = setup_view(CreateUserView, request)
        v.post(v, request)

        # create p2
        form_data_p2 = {'username': 'patron2',
                        'status': "professor",
                        'privileges': "no privileges",
                        'email': 'p2@mail.ru',
                        'address': 'Via Sacra, 13',
                        'phone_number': '30002',
                        'first_name': 'Nadia',
                        'last_name': 'Teixeira',
                        'password1': '12356qwerty',
                        'password2': '12356qwerty',
                        'submit': 'Submit'
                        }

        request.POST = form_data_p2
        v = setup_view(CreateUserView, request)
        v.post(v, request)

        # create p3
        form_data_p3 = {'username': 'patron3',
                        'status': "professor",
                        'privileges': "no privileges",
                        'email': 'p3@mail.ru',
                        'address': 'Via del Corso, 22',
                        'phone_number': '30003',
                        'first_name': 'Elvira',
                        'last_name': 'Espindola',
                        'password1': '2356qwerty',
                        'password2': '2356qwerty',
                        'submit': 'Submit'
                        }

        request.POST = form_data_p3
        v = setup_view(CreateUserView, request)
        v.post(v, request)

        # create v
        form_data_v = {'username': 'patron5',
                       'status': "visiting professor",
                       'privileges': "no privileges",
                       'email': 'v@mail.ru',
                       'address': 'Stret Atocha, 27',
                       'phone_number': '30005',
                       'first_name': 'Veronika',
                       'last_name': 'Rama',
                       'password1': '2356qwerty',
                       'password2': '2356qwerty',
                       'submit': 'Submit'
                       }

        request.POST = form_data_v
        v = setup_view(CreateUserView, request)
        v.post(v, request)

        for i in User.objects.all():
            print(i)
        self.assertEqual(len(User.objects.all()), 9)


        # l2 checks information of the system
        # -----------------------------------

    # def test_TC5(self):
    #     self.test_TC4()
    #
    #     request = HttpRequest
    #     request.method = "POST"
    #     request.user = self.l3
    #     doc = get_doc(request, self.d1.id)
    #
    #     fields = get_fields_of(doc)
    #     fields = dict(fields)
    #
    #     num_of_copies = int(fields['copies'])
    #     num_of_copies -= 1
    #     fields['copies'] = str(num_of_copies)
    #     fields['submit'] = 'Submit'
    #
    #     request.method = "POST"
    #     request.POST = fields
    #     response = update_doc(request, self.d1.id)
    #
    #     self.assertEqual(self.d1.copies, 2)

    # def test_TC6(self):
    #     self.test_TC4()
    #
    #     # p1 leaves a request for a book d3
    #     request = HttpRequest()
    #     request.method = "GET"
    #     request.user = self.p1
    #     request.GET['doc'] = self.d3.id
    #     make_new(request)
    #
    #     # p2 leaves a request for a book d3
    #     request.user = self.p2
    #     request.GET['doc'] = self.d3.id
    #     make_new(request)
    #
    #     # s leaves a request for a book d3
    #     request.user = self.s
    #     request.GET['doc'] = self.d3.id
    #     make_new(request)
    #
    #     # v leaves a request for a book d3
    #     request.user = self.v
    #     request.GET['doc'] = self.d3.id
    #     make_new(request)
    #
    #     # p3 leaves a request for a book d3
    #     request.user = self.p3
    #     request.GET['doc'] = self.d3.id
    #     make_new(request)
    #
    #     # now librarian should approve requests
    #     request = HttpRequest()
    #     request.method = "GET"
    #     request.user = self.librarian
    #
    #     # approve 1st (p1 d3)
    #     request.GET['req_id'] = self.p1.request_set.get(doc=self.d3).id
    #     request.GET['user_id'] = self.p1.id
    #     approve_request(request)
    #
    #     # approve 2nd (p2 d3)
    #     request.GET['req_id'] = self.p2.request_set.get(doc=self.d3).id
    #     request.GET['user_id'] = self.p2.id
    #     approve_request(request)
    #
    #     # approve 3rd (s d3)
    #     request.GET['req_id'] = self.s.request_set.get(doc=self.d3).id
    #     request.GET['user_id'] = self.s.id
    #     approve_request(request)
    #
    #     # librarian places an outstanding request on d3
    def test_TC7(self):
        pass

    # def test_TC8(self):
    #     datafile = open('data.log', 'r')
    #     datafile.write('')  # clear all logs before making changes in system
    #     self.test_TC6()
    #     data = datafile.readlines()
    #     datafile.close()
    #     all_in = lambda x, y: all([item in y for item in x])  # check that all items of x are in y
    #     self.assertTrue(all_in(['admin1', 'created', 'l1'], data[0]))
    #     self.assertTrue(all_in(['admin1', 'created', 'l2'], data[1]))
    #     self.assertTrue(all_in(['admin1', 'created', 'l3'], data[2]))
    #     self.assertTrue(all_in(['l2', 'updated', self.d1.title], data[3]))
    #     self.assertTrue(all_in(['l2', 'updated', self.d2.title], data[4]))
    #     self.assertTrue(all_in(['l2', 'updated', self.d3.title], data[5]))
    #     self.assertTrue(all_in(['l2', 'created', 's'], data[6]))
    #     self.assertTrue(all_in(['l2', 'created', 'p1'], data[7]))
    #     self.assertTrue(all_in(['l2', 'created', 'p2'], data[8]))
    #     self.assertTrue(all_in(['l2', 'created', 'p3'], data[9]))
    #     self.assertTrue(all_in(['l2', 'created', 'v'], data[10]))
    #     self.assertTrue(all_in(['p1', 'approved request', self.d3.title], data[11]))
    #     self.assertTrue(all_in(['p2', 'approved request', self.d3.title], data[12]))
    #     self.assertTrue(all_in(['s', 'approved request', self.d3.title], data[13]))
    #     self.assertTrue(all_in(['v', 'approved request', self.d3.title], data[14]))
    #     self.assertTrue(all_in(['p3', 'approved request', self.d3.title], data[15]))
    #
    # def test_TC9(self):
    #     datafile = open('data.log', 'r')
    #     datafile.write('')  # clear all logs before making changes in system
    #     self.test_TC7()
    #     data = datafile.readlines()
    #     datafile.close()
    #     all_in = lambda x, y: all([item in y for item in x])  # check that all items of x are in y
    #     self.assertTrue(all_in(['admin1', 'created', 'l1'], data[0]))
    #     self.assertTrue(all_in(['admin1', 'created', 'l2'], data[1]))
    #     self.assertTrue(all_in(['admin1', 'created', 'l3'], data[2]))
    #     self.assertTrue(all_in(['l2', 'updated', self.d1.title], data[3]))
    #     self.assertTrue(all_in(['l2', 'updated', self.d2.title], data[4]))
    #     self.assertTrue(all_in(['l2', 'updated', self.d3.title], data[5]))
    #     self.assertTrue(all_in(['l2', 'created', 's'], data[6]))
    #     self.assertTrue(all_in(['l2', 'created', 'p1'], data[7]))
    #     self.assertTrue(all_in(['l2', 'created', 'p2'], data[8]))
    #     self.assertTrue(all_in(['l2', 'created', 'p3'], data[9]))
    #     self.assertTrue(all_in(['l2', 'created', 'v'], data[10]))
    #     self.assertTrue(all_in(['p1', 'approved request', self.d3.title], data[11]))
    #     self.assertTrue(all_in(['p2', 'approved request', self.d3.title], data[12]))
    #     self.assertTrue(all_in(['s', 'approved request', self.d3.title], data[13]))
    #     self.assertTrue(all_in(['v', 'approved request', self.d3.title], data[14]))
    #     self.assertTrue(all_in(['p3', 'approved request', self.d3.title], data[15]))
    #     self.assertTrue(all_in(['l3', 'outstanding request', self.d3.title], data[16]))
    #     self.assertTrue(all_in(['l3', 'waiting list deleted', self.d3.title], data[17]))

    def test_TC10(self):
        pass

    def test_TC11(self):
        pass

    def test_TC12(self):
        pass

