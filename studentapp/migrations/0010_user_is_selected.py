# Generated by Django 5.1.4 on 2025-02-26 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentapp', '0009_bookmarked_session'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_selected',
            field=models.BooleanField(default=False),
        ),
    ]
