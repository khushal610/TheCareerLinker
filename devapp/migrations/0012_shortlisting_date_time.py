# Generated by Django 5.1.4 on 2025-02-26 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devapp', '0011_shortlisting'),
    ]

    operations = [
        migrations.AddField(
            model_name='shortlisting',
            name='date_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
