# Generated by Django 5.0.6 on 2024-05-23 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rifas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rifa',
            name='codigo',
            field=models.CharField(max_length=3, unique=True),
        ),
    ]
