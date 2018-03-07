import os
import sys
import psutil
import logging
import datetime


from django.apps import apps
from django.db import models
import django
from innopolka import settings
settings.configure()
django.setup()

Book = apps.get_model('Book')
print(Book.objects.all())



def reboot():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """
    try:
        p = psutil.Process(os.getpid())
        f = p.open_files() + p.connections()
        for handler in f:
            os.close(handler.fd)
    except Exception as e:
        logging.error(e)

    python = sys.executable
    os.execl(python, python, 'tc9.py')


def create_new_book(title='b1'):
    print('happens')
    # Book = apps.get_model('Documents', 'Book')


def clear_book(title='b1'):
    pass


if __name__ == '__main__':
    if len(sys.argv) > 1:
        create_new_book()
        reboot()
        # check book in db
        clear_book()
    else:
        exit(1)

