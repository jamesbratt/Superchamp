# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-01 21:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('routes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='created_date',
            field=models.DateTimeField(default=None, verbose_name='date published'),
        ),
        migrations.AddField(
            model_name='route',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]