# Generated by Django 2.2.19 on 2021-03-25 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etabotapp', '0005_celerytask_meta_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='celerytask',
            name='task_id',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
