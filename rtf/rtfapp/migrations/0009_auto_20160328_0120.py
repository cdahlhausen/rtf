# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rtfapp', '0008_parcel_distance_to_trail'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcel',
            name='notes',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AddField(
            model_name='parcel',
            name='permissions',
            field=models.CharField(default=None, max_length=255),
        ),
    ]
