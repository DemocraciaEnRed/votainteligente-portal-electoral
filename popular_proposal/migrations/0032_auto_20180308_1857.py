# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-08 18:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('popular_proposal', '0031_popularproposal_one_liner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='popularproposal',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='proposaltemporarydata',
            name='organization',
        ),
    ]