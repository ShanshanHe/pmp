# Generated by Django 2.2.28 on 2022-10-24 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etabotapp', '0007_auto_20210415_0149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauth1token',
            name='oauth_token',
            field=models.CharField(max_length=2000),
        ),
        migrations.AlterField(
            model_name='oauth1token',
            name='oauth_token_secret',
            field=models.CharField(max_length=2000),
        ),
    ]