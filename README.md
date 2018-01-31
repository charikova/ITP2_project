# innopolka
Library Management System website: Introduction to Programming project by students of BS1-7 group, team: Danil Ginzburg, 

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
<img src="">

