from django.db import models
from Documents.models import Document
from django.contrib.auth.models import User


class Request(models.Model):
    doc = models.ForeignKey(Document, null=True, default=None, on_delete=models.CASCADE)
    checked_up_by_whom = models.ForeignKey(User, null=True, default=None, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.doc)
