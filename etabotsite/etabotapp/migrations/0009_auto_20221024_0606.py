# Generated by Django 2.2.28 on 2022-10-24 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etabotapp', '0008_auto_20221024_0535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauth1token',
            name='oauth_token',
            field=models.CharField(max_length=2048),
        ),
        migrations.AlterField(
            model_name='oauth1token',
            name='oauth_token_secret',
            field=models.CharField(max_length=2048),
        ),
        migrations.AlterField(
            model_name='oauth2token',
            name='refresh_token',
            field=models.CharField(max_length=2048, null=True),
        ),
    ]