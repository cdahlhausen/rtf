# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rtfapp.models


def create_default_status(apps, schema_editor):
    ParcelStatus = apps.get_model("rtfapp", "ParcelStatus")
    unassigned = ParcelStatus(label="Uncategorized", color='#00aaee')
    unassigned.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rtfapp', '0010_remove_parcel_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParcelStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255)),
                ('color', models.CharField(max_length=7)),
            ],
        ),
        migrations.RunPython(create_default_status),
        migrations.AddField(
            model_name='parcel',
            name='color',
            field=models.CharField(default=b'', max_length=7, blank=True),
        ),
        migrations.AddField(
            model_name='parcel',
            name='status',
            field=models.ForeignKey(default=1, to='rtfapp.ParcelStatus'),
            preserve_default=False
        ),
    ]
