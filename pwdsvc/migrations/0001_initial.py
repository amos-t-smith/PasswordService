# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-22 06:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('name', models.CharField(max_length=32)),
                ('uid', models.IntegerField(primary_key=True, serialize=False)),
                ('comment', models.TextField()),
                ('home', models.TextField()),
                ('shell', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('name', models.CharField(max_length=31)),
                ('gid', models.IntegerField(primary_key=True, serialize=False)),
                ('members', models.ManyToManyField(to='pwdsvc.Account')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='gid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pwdsvc.Group'),
        ),
    ]