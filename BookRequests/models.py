from django.db import models
from Documents.models import Document
from django.contrib.auth.models import User


class Request(models.Model):
    doc = models.ForeignKey(Document, null=True, default=None, on_delete=models.CASCADE)
    users = models.ManyToManyField(User)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.doc.title) + ", users: " + ' '.join([str(user.username) for user in self.users.all()])
