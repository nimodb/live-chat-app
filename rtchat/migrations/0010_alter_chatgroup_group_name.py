# Generated by Django 5.0.7 on 2024-08-11 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtchat', '0009_alter_chatgroup_group_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatgroup',
            name='group_name',
            field=models.CharField(blank=True, max_length=128, unique=True),
        ),
    ]
