# Generated by Django 5.1.4 on 2025-03-05 01:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devapp', '0021_quizcategory_is_course_quiz'),
    ]

    operations = [
        migrations.AddField(
            model_name='course_module_content',
            name='course_quiz',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='devapp.quizcategory'),
        ),
    ]
