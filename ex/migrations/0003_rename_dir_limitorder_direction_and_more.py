# Generated by Django 5.1.2 on 2024-12-01 13:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ex", "0002_rename_is_positions_initialized_depo_is_init_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="limitorder",
            old_name="dir",
            new_name="direction",
        ),
        migrations.RenameField(
            model_name="marketorder",
            old_name="dir",
            new_name="direction",
        ),
        migrations.RenameField(
            model_name="stoporder",
            old_name="dir",
            new_name="direction",
        ),
        migrations.RenameField(
            model_name="takeorder",
            old_name="dir",
            new_name="direction",
        ),
        migrations.RenameField(
            model_name="triggerorder",
            old_name="dir",
            new_name="direction",
        ),
    ]
