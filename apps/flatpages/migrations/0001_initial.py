# Generated by Django 2.1 on 2018-10-08 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FlatPage',
            fields=[
                ('slug', models.CharField(max_length=80, primary_key=True, serialize=False, unique=True)),
                ('content', models.TextField()),
            ],
        ),
    ]
