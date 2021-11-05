# Generated by Django 3.2.9 on 2021-11-05 14:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0011_alter_market_answer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guess',
            name='value',
            field=models.FloatField(help_text="User's guess", validators=[django.core.validators.MinValueValidator(1e-06), django.core.validators.MaxValueValidator(1000000)]),
        ),
    ]
