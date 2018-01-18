from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

from django.db import models

from routes.models import Route


class ChallengeTime(models.Model):
    """A model that describes a ride time."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, default=None)
    duration = models.FloatField()
    duration_str = models.CharField(max_length=100, null=True)
    average_speed = models.FloatField()
    performance = models.FloatField(default=None)
    data = JSONField()
    hit_target = models.BooleanField(default=False)
    created_date = models.DateTimeField('date published')

    def __str__(self):
        return self.user.username + ' - ' + self.route.title
