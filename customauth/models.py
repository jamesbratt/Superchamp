from __future__ import unicode_literals
from django.contrib.auth.models import User

from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    activation_key = models.CharField(max_length=200)
    key_expires = models.DateTimeField()
    is_organiser = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
