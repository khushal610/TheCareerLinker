# Generated by Django 5.1.4 on 2025-03-21 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devapp', '0026_response_student_query'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate_details',
            name='name_on_certificate',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
