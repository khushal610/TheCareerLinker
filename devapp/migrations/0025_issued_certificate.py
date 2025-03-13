# Generated by Django 5.1.4 on 2025-03-10 01:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devapp', '0024_certificate_details_dev_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Issued_Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('digital_signature', models.CharField(blank=True, max_length=255, null=True)),
                ('certificate_details', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='devapp.certificate_details')),
                ('course_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='devapp.online_certification_course')),
                ('student_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
