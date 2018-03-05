from django.test import TestCase
from UserCards.models import UserProfile
from django.http import HttpRequest, Http404
from .models import *
from BookRequests.views import make_new, approve_request
import BookRequests
import datetime
from UserCards.views import user_card_info


class Delivery1(TestCase):

    def test_TC1(self):
        #  initial state
        p = User.objects.create_user('username', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=p, phone_number=123, status='student', address='1-103')
        l = User.objects.create_user('username2', 'exampl@mail.ru', '123456qwerty', first_name='F', last_name='L', is_staff=True)
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
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L', is_staff=True)
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
        should_be_today = returning_date - datetime.timedelta(days=28) # 4 weeks = 28 days
        should_be_today = datetime.date(year=should_be_today.year, month=should_be_today.month, day=should_be_today.day)

        self.assertEqual(should_be_today, datetime.date.today())

    def test_TC4(self):
        #
        f = User.objects.create_user('Faculty', 'fac@mail.ru', '123456qwerty', first_name='F', last_name='L')
        UserProfile.objects.create(user=f, status='faculty', phone_number=896000, address='2-107')

        s = User.objects.create_user('Student', 'stu@mail.ru', '123456qwerty', first_name='S', last_name='L')
        UserProfile.objects.create(user=s, status='student', phone_number=796001, address='2-110')

        l = User.objects.create_user('Librarian', 'stu@mail.ru', '123456qwerty', first_name='S', last_name='L', is_staff=True)
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
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L', is_staff=True)

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

        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',is_staff=True)
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
                                   edition=1, copies=1, authors='sadf', cover='cover', publisher='pub', is_bestseller=True)

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

        student.documentcopy_set.get(id=A.id) # will raise error if copy of A doesn't exist

class Delivery2(TestCase):

    def test_TC1(self):
        librarian = User.objects.create_user('l', 'exampl23@mail.ru', '123456qwerty', first_name='F', last_name='L',
                                             is_staff=True)
        b1 = Book.objects.create(title='Introduction to Algorithms', price=0, publication_date='2009',
                                 edition=3, copies=3, authors='Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest and '
                                                             'Clifford Stein', cover='cover', publisher='MIT Press')
        b2 = Book.objects.create(title='Design Patterns: Elements of Reusable Object-Oriented Software', price=0,
                                 publication_date='2003', edition=1, copies=2,
                                 authors='Erich Gamma, Ralph Johnson, John Vlissides, Richard Helm', cover='cover',
                                 publisher='Addison-Wesley Professional', is_bestseller=True)
        b3 = Book.objects.create(title='The Mythical Man-month', price=0, publication_date='1995', edition=2, copies=1,
                                 authors='Brooks,Jr., Frederick P.', cover='cover', publisher='Addison-Wesley Longman Publishing '
                                 'Co., Inc.', is_reference=True)

        av1=AVFile.objects.create(title='Null References: The Billion Dollar Mistake', authors='Tony Hoare')
        av2 = AVFile.objects.create(title=': Information Entropy', authors='Claude Shannon')

        p1 = User.objects.create_user('f', 'exampl2@mail.ru', '123456qwerty', first_name='Sergey', last_name='Afonso')
        UserProfile.objects.create(user=p1, phone_number=30001, status='faculty', address='Via Margutta, 3')

        p2 = User.objects.create_user('s', 'exampl2@mail.ru', '123456qwerty', first_name='Nadia', last_name='Teixeira')
        UserProfile.objects.create(user=p2, phone_number=30002, status='student', address='Via Sacra, 13')

        p3 = User.objects.create_user('s', 'exampl2@mail.ru', '123456qwerty', first_name='Elvira', last_name='Espindola')
        UserProfile.objects.create(user=p2, phone_number=30003, status='student', address='Via del Corso, 22')

