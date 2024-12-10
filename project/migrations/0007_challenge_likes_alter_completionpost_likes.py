# Generated by Django 5.1.2 on 2024-12-10 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_challenge_image_alter_completionpost_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_challenges', to='project.userprofile'),
        ),
        migrations.AlterField(
            model_name='completionpost',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_completion_posts', to='project.userprofile'),
        ),
    ]