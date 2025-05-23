# Generated by Django 5.1.4 on 2025-02-24 06:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devapp', '0010_online_sessions'),
        ('studentapp', '0008_attempted_session'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmarked_session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_bookmarked', models.BooleanField(default=False)),
                ('session_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='devapp.online_sessions')),
                ('student_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
