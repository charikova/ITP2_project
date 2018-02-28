# innopolka
Python-Django implemetion of Library Management System website: 
Introduction to Programming project by students of BS1-7 group, team: Danil Ginzburg, Nikita Nigmatulin,
Maria Charikova, Roman Bogachev

# The way it works
Patrons can survey diffrent documents on the main page and leave requests for them. Librarins (staff) can whether 
approve or refuse their requests. 

# Usage
## Installation
After you installation of django framework via
     
     pip3 install django
## Running
You can simply run website using fallowing command

     python manage.py runserver    #In case you have python2 and python3 run: python3 manage.py runserver    
     
## Sign in/up
In order to create new admin(admin has all permissions of librarian and even more) run

     python manage.py createsuperuser
     
Fill out all required fields and get logged-in in website

## Testing
We have some unit tests, which are needed to suit all requirements. They are placed in Documents/tests.py. Execute those via

     python manage.py test Documents.tests.Delivery1 # Use Delivery[number of delivery] to run one of the deliveries test


# Architecture of the website
![alt text](https://github.com/charikova/innopolka/blob/master/architecture%20project.png)
# Implementation
## Documents
We store all documents in sqlite3 db provided by default by django framework. 
Table 

    class Document(models.Model):
          '''
          Base class for all documents
          '''
          title = models.CharField(max_length=250)
          price = models.IntegerField()
          keywords = models.CharField(max_length=250)
          authors = models.CharField(max_length=250)
          cover = models.CharField(max_length=1000)
          copies = models.PositiveIntegerField(default=1)
          type = models.CharField(max_length=100, default='Document')

which is typicly the abstract class for all documents. It has necessary fields for all document types which are 
required to fill out when librarian is creating new document.
Bellow in innopolka/Documents/models.py we have other document types which are inhereted from 
Document model class. It looks like this: 

     class YourType(Document):
          type = "Your Type"
          field1 = models.CharField(max_length=255)
          filed2 = models.IntegerField()
          
Notice, that each inherited document should have "type" attribute that will be used as a name for 
creation this kind of document. 

# Users 
     <ul>
       <li> Student </li>Have permission to <strong>Check out</strong> documents for 3 weeks and is able to renew documents
       <li> Faculty </li>Have permission to <strong>Check out</strong> documents for 4 weeks and is able to renew documents
       <li> Librarian </li>Is allowed to add/delete/update any document. Can add/del/modify patrons and their permissions as well.
     </ul>

We are using <a href="https://docs.djangoproject.com/en/2.0/topics/auth/">built-in user model</a> provied by 
django framework. This model have common user's fields like username, password, email and etc. But in order 
to keep extra information of users (phone number, status, etc) we would need "UserProfile" model. This model
is created every time whenever new user is created, so it allows us to store any data of user we would like.

     class UserProfile(models.Model):
         user = models.OneToOneField(User, on_delete=models.CASCADE) # link to user with OnoToOne-connection
         phone_number = models.CharField(max_length=15, null=True, blank=True)
         address = models.CharField(max_length=250, null=True, blank=True)
         photo = models.ImageField(default="https://lh3.googleusercontent.com/")
         status = models.CharField(max_length=250, default='student')
         
         
## Librarian features
Librarian is a user which has is_staff flag equal to True. This flag allows librarians to use special features
defined in Documents/librarian_view.py. Nevertheless those features are availale for everyone, only 
librarians have permissions to execute it. "required_staff" function limit non-staff users to deal with database
and other users. For example feature del_doc which deletes document form database

     @required_staff
     def del_doc(request, id):
         doc = Document.objects.get(id=id)
         doc.delete()
         return redirect('/')


                     
 ## html rendering
 In depence on user's permissions django renders html in different way. 
 All html files have special django insertions (syntax is similar to python code)
 
     {% if user.is_anonymous %} # execute if user is guest
          <a href="/user/login"> Log In </a>
     {% elif user.is_authenticated %} # execute if user is not a guest
          <a href="/user/"> {{user.username}} </a>
          <a href="/user/logout"> Log Out </a>
     {% endif %}
     {% if user.is_staff %} # execute if user is librarian
          <a href="/add_doc/">Add document</a>
     {% endif %}
         
## Booking System (Document Copy)
    class DocumentCopy(models.Model):
    """
    copy object which is created when user check out document
    """
    doc = models.ForeignKey(Document, blank=True, default=None, on_delete=models.CASCADE) # link to document which is checked out
    checked_up_by_whom = models.ForeignKey(User, blank=True, default=None, on_delete=models.CASCADE) # link to holder
    level = models.PositiveIntegerField(default=1)
    room = models.PositiveIntegerField(default=1)

Every time user check out document - new copy object is created. Basicly it is not a document, it is
an object that keeps links to particluar document and to holder of this document. Also DocumentCopy
keeps other data like level, room, time it was checked out, etc.

## Return system
    @required_staff
    def return_doc(request):
        """
        taking document back (user has returned his document)
        """
        try:
            copy_instance = documents_models.DocumentCopy.objects.get(pk=request.GET.get('copy_id'))
        except:
            return redirect('/')
        user_id = copy_instance.checked_up_by_whom.id
        copy_instance.doc.copies += 1
        copy_instance.doc.save()
        copy_instance.delete()
        return redirect('/user?id=' + str(user_id))

Only librarian can approve that a book has been returned, thus only librarian can see "return book" button. Every time this button
is pressed the document copy object is deleted and number of available copies of the document is increased by 1.



