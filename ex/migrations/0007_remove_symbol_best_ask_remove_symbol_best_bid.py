# Generated by Django 5.1.2 on 2024-12-23 08:53

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ex", "0006_limitorder_is_init_marketorder_is_init_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="symbol",
            name="best_ask",
        ),
        migrations.RemoveField(
            model_name="symbol",
            name="best_bid",
        ),
    ]
