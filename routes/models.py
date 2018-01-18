from __future__ import unicode_literals

from django.contrib.auth.models import User

from django.db import models


class Route(models.Model):
    """A model that describes a cycle route"""

    EASY = 'EA'
    MODERATE = 'MO'
    TOUGH = 'TO'

    DIFFICULTY_CHOICES = (
        (EASY, 'Easy'),
        (MODERATE, 'Moderate'),
        (TOUGH, 'Tough'),
    )

    UK = 'GB'
    FRANCE = 'FR'
    ITALY = 'IT'
    SPAIN = 'ES'
    GERMANY = 'DE'

    COUNTRY_CHOICES = (
        (UK, 'United Kingdom'),
        (FRANCE, 'France'),
        (ITALY, 'Italy'),
        (SPAIN, 'Spain'),
        (GERMANY, 'Germany'),
    )

    title = models.CharField(max_length=200)
    polyline = models.TextField()
    distance = models.FloatField()
    start_lat = models.CharField(max_length=100)
    start_long = models.CharField(max_length=100)
    finish_lat = models.CharField(max_length=100)
    finish_long = models.CharField(max_length=100)
    min_elevation = models.FloatField()
    max_elevation = models.FloatField()
    elevation_gain = models.FloatField()
    difficulty = models.CharField(
        max_length=2,
        choices=DIFFICULTY_CHOICES,
    )
    country = models.CharField(
        max_length=2,
        choices=COUNTRY_CHOICES,
    )
    locality = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None,)
    created_date = models.DateTimeField('date published', default=None,)

    def __str__(self):
        return self.title
