# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-04-18 14:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('popular_proposal', '0033_popular_proposal_multiple_sites'),
    ]

    operations = [
        migrations.AddField(
            model_name='commitment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='commitment',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
