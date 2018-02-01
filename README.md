# innopolka
Python-Django implemetion of Library Management System website: 
Introduction to Programming project by students of BS1-7 group, team: Danil Ginzburg, Nikita Nigmatulina,
Maria Charikova, Roman

# The way it works
Patrons can survey diffrent documents on the main page <strong>/index.html</strong> and leave requests for them. Librarins (staff) can whether 
approve or refuse their requests. 

# Usage
After installation you can simply run this website by runnign this

     python manage.py runserver # or python3 manage.py runserver if you have python2 and python3
     
command in your command line

# Patron's types
There are types of patrons available: 
<ul>
  <li> Student </li>
  <li> Faculty </li>
</ul>

## Student
Have permission to <strong>Check out</strong> documents for 3 weeks and are able to renew documents
## Faculty
Have permission to <strong>Check out</strong> documents for 4 weeks and are able to renew documents
# Librarian permissions
Librarians are allowed to add/delete/update any document. They can modify patrons and their permissions as well.
Librarians <strong>are not</strong> allowed to check out documents: only approve/refuse current requests for documents from 
patron's requests list on /requests url
  
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
Document model class. It look like this: 

     class YourType(Document):
          type = "Your Type"
          field1 = models.CharField(max_length=255)
          filed2 = models.IntegerField()
          
Notice, that each inherited document should have "type" attribute that will be used as a name for 
creation this type of document. The thing is when document's type is created in db, the name of 
class disappears.
<strong>Important!</strong> when you will modify models.py code you should run

     python manage.py makemigrations & python manage.py migrate
     
in order to apply your changes into database.
## Document Copy
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
## Users(Patons)
We are using <a href="https://docs.djangoproject.com/en/2.0/topics/auth/">built-in user authentication</a> provied by django framework
