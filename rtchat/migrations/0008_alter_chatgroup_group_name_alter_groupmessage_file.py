# Generated by Django 5.0.7 on 2024-07-31 11:03

import shortuuid.main
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtchat', '0007_groupmessage_file_alter_chatgroup_group_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatgroup',
            name='group_name',
            field=models.CharField(blank=True, default=shortuuid.main.ShortUUID.uuid, max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='groupmessage',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='files/'),
        ),
    ]
