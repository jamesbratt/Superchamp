# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-01-18 22:14
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('routes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChallengeTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.FloatField()),
                ('duration_str', models.CharField(max_length=100, null=True)),
                ('average_speed', models.FloatField()),
                ('performance', models.FloatField(default=None)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('hit_target', models.BooleanField(default=False)),
                ('start_time', models.DateTimeField()),
                ('created_date', models.DateTimeField(verbose_name='date published')),
                ('route', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='routes.Route')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
