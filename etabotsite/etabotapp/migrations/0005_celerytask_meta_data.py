# Generated by Django 2.2.19 on 2021-03-13 16:57

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('etabotapp', '0004_celerytask'),
    ]

    operations = [
        migrations.AddField(
            model_name='celerytask',
            name='meta_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]
