# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rtfapp', '0009_auto_20160328_0120'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parcel',
            name='status',
        ),
    ]
