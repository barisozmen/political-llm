# Generated by Django 5.1.2 on 2025-05-29 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="is_email_verified",
        ),
    ]
