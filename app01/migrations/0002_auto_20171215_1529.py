# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-15 07:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='email',
            field=models.EmailField(default=1, max_length=254),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='password',
            field=models.CharField(default=1, max_length=64),
        ),
    ]
