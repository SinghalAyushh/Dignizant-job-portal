# Generated by Django 3.0 on 2021-04-19 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobapp', '0018_auto_20210419_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='image',
            field=models.ImageField(upload_to='upload/'),
        ),
    ]
