# Generated by Django 5.1.2 on 2024-11-21 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ex', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='depo',
            old_name='is_positions_initialized',
            new_name='is_init',
        ),
        migrations.AddField(
            model_name='depo',
            name='risk_rate',
            field=models.FloatField(default=0),
        ),
    ]