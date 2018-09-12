# Generated by Django 2.1 on 2018-09-07 12:08

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rides', '0002_complaint'),
    ]

    operations = [
        migrations.CreateModel(
            name='RideComplaint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('date_time', models.DateTimeField(default=datetime.datetime(2018, 9, 7, 12, 8, 6, 635503, tzinfo=utc))),
                ('status', models.CharField(choices=[('new', 'New'), ('considered', 'Considered'), ('confirmed', 'Confirmed'), ('disapproved', 'Disapproved')], default='new', max_length=10)),
                ('ride', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complaints', to='rides.Ride')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='complaints', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='ride',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='user',
        ),
        migrations.DeleteModel(
            name='Complaint',
        ),
    ]
