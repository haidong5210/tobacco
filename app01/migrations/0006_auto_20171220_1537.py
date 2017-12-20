# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-20 07:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0005_auto_20171220_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='gender',
            field=models.IntegerField(choices=[(1, '男'), (2, '女')], default=1, verbose_name='性别'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='host',
            field=models.ManyToManyField(to='app01.Host', verbose_name='主机'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.UserType', verbose_name='类型'),
        ),
    ]