# Generated by Django 2.1.3 on 2019-11-11 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etabotapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauth2coderequest',
            name='timestamp',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='oauth2token',
            name='expires_at',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='oauth2token',
            name='refresh_token',
            field=models.CharField(max_length=200, null=True),
        ),
    ]