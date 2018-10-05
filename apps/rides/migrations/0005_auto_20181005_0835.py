# Generated by Django 2.1 on 2018-10-05 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rides', '0004_auto_20181002_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='ride',
            name='cancel_reason',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='ridebooking',
            name='cancel_reason',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='ridebooking',
            name='status',
            field=models.CharField(choices=[('created', 'Created'), ('payed', 'Payed'), ('canceled', 'Canceled'), ('revoked', 'Revoked')], default='created', max_length=10),
        ),
    ]
