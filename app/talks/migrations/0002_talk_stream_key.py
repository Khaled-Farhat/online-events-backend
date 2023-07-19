# Generated by Django 4.1.7 on 2023-07-18 00:05

from django.db import migrations, models
import django.utils.crypto
import functools


class Migration(migrations.Migration):
    dependencies = [
        ("talks", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="talk",
            name="stream_key",
            field=models.CharField(
                default=functools.partial(
                    django.utils.crypto.get_random_string, *(20,), **{}
                ),
                max_length=20,
                unique=True,
            ),
        ),
    ]
