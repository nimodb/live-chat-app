# Generated by Django 5.0.7 on 2024-07-31 09:40

import shortuuid.main
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtchat', '0006_alter_groupmessage_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupmessage',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='file/'),
        ),
        migrations.AlterField(
            model_name='chatgroup',
            name='group_name',
            field=models.CharField(blank=True, default=shortuuid.main.ShortUUID.uuid, max_length=128, unique=True),
        ),
    ]
