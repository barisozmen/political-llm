# Generated by Django 5.1.2 on 2025-05-29 09:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "avatar",
                    models.ImageField(blank=True, null=True, upload_to="avatars/"),
                ),
                ("bio", models.TextField(blank=True, max_length=500)),
                ("website", models.URLField(blank=True)),
                (
                    "twitter_handle",
                    models.CharField(
                        blank=True,
                        help_text="Twitter username without @",
                        max_length=50,
                    ),
                ),
                (
                    "discord_handle",
                    models.CharField(
                        blank=True, help_text="Discord username", max_length=50
                    ),
                ),
                (
                    "eth_address",
                    models.CharField(
                        blank=True, help_text="Ethereum wallet address", max_length=42
                    ),
                ),
                (
                    "bitcoin_address",
                    models.CharField(
                        blank=True, help_text="Bitcoin wallet address", max_length=62
                    ),
                ),
                ("is_email_verified", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
