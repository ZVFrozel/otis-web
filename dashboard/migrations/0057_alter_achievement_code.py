# Generated by Django 3.2.7 on 2021-09-17 16:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0056_auto_20210917_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='code',
            field=models.CharField(max_length=96, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='24-char hex string', regex='^[a-f0-9]{24}$')]),
        ),
    ]