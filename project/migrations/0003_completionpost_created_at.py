# Generated by Django 5.1.2 on 2024-12-08 19:01

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_challenge_completed_on_challenge_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='completionpost',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
