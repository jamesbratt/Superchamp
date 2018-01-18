# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-22 19:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0002_auto_20171001_2129'),
        ('challenges', '0010_remove_challengetime_challenges'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='challenge',
        ),
        migrations.AddField(
            model_name='participant',
            name='route',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='routes.Route'),
        ),
    ]