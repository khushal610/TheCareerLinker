# Generated by Django 5.1.4 on 2025-03-02 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devapp', '0019_online_certification_course_course_summary_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='online_certification_course',
            name='is_launched',
            field=models.BooleanField(default=False),
        ),
    ]
