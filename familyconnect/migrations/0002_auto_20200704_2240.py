# Generated by Django 3.0.8 on 2020-07-04 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('familyconnect', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='app',
            name='app_id',
        ),
        migrations.AddField(
            model_name='app',
            name='channel_name',
            field=models.TextField(null=True),
        ),
    ]
