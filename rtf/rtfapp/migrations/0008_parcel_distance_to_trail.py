# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        # ('rtfapp', '0007_auto_20160207_1416'),
        ('rtfapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcel',
            name='distance_to_trail',
            field=models.FloatField(default=100000),
            preserve_default=False,
        ),
    ]
