# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-30 08:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0005_remove_challengetime_is_performance_negative'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='target_time_str',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
