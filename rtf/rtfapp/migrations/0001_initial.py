# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Atom',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('coordinates', models.TextField()),
                ('last_edit', models.DateTimeField(auto_now_add=True)),
                ('segment_id', models.IntegerField()),
                ('position_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='IntersectionTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started', models.DateTimeField(auto_now_add=True)),
                ('finished', models.DateTimeField(null=True, blank=True)),
                ('placemarks', models.IntegerField()),
                ('placemarks_completed', models.IntegerField()),
                ('placemark_avg_time', models.DurationField(null=True)),
                ('parcels_extracted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='MaintenanceRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
                ('submit_timestamp', models.DateTimeField(auto_now_add=True)),
                ('resolved_timestamp', models.DateTimeField(null=True, blank=True)),
                ('resolved', models.BooleanField(default=False)),
                ('created_by', models.TextField()),
                ('location', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pid', models.CharField(max_length=16)),
                ('size', models.DecimalField(default=0.0, max_digits=10, decimal_places=5)),
                ('owner', models.TextField()),
                ('points_string', models.TextField()),
                ('parcel_type', models.CharField(max_length=255)),
                ('status', models.CharField(default=None, max_length=255)),
                ('address', models.TextField(default=None)),
                ('on_trail', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_edit', models.DateTimeField(auto_now_add=True)),
                ('expiration_date', models.DateTimeField()),
                ('path_to_doc', models.TextField()),
                ('summary', models.TextField()),
                ('parcel', models.ForeignKey(to='rtfapp.Parcel')),
            ],
        ),
        migrations.CreateModel(
            name='TrailSegment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
                ('difficulty', models.IntegerField(default=0)),
                ('name', models.TextField()),
                ('last_edit', models.DateTimeField(auto_now_add=True)),
                ('trail_status', models.CharField(default=b'Open', max_length=10, choices=[(b'Open', b'Open'), (b'Closed', b'Closed')])),
                ('current_conditions', models.TextField()),
                ('style_url', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('phone_number', models.CharField(max_length=15)),
                ('email', models.CharField(max_length=255, null=True, blank=True)),
                ('password_hash', models.CharField(max_length=512, null=True, blank=True)),
                ('forgot_password_hash', models.CharField(max_length=512, null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='atom',
            name='parcel',
            field=models.ForeignKey(blank=True, to='rtfapp.Parcel', null=True),
        ),
        migrations.AddField(
            model_name='atom',
            name='trail_segment',
            field=models.ForeignKey(to='rtfapp.TrailSegment'),
        ),
    ]
