# Generated by Django 5.1.4 on 2025-03-17 06:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devapp', '0025_issued_certificate'),
        ('studentapp', '0017_course_enrollment_razorpay_order_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student_Course_Query',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_query_content', models.TextField(blank=True, null=True)),
                ('course_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='devapp.online_certification_course')),
                ('document_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='devapp.course_module_content')),
                ('student_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
