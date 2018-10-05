# Generated by Django 2.1 on 2018-09-24 05:07
from dbmail.models import MailTemplate
from django.db import migrations


def load_mail_template(apps, schema_editor):
    MailTemplate.objects.create(
        name="Rate the ride",
        subject="You can rate the ride {{ ride }}",
        message="""
            <p></p>
            <p>You can rate the ride {{ ride }} and driver 
            {{ driver.first_name }} {{ driver.last_name }}<br>
            <b>Date:</b> {{ ride.date_time }}<br>
            <b>Car:</b> {{ ride.car }}<br>
            <b>Number of sits:</b> {{ ride.number_of_sits }}<br>
            <b>Description:</b> {{ ride.description }}<br>
            Using this link: _______
            </p>
            <p>Thanks for using our site!</p>
            <p>The {{ site_name }} team</p>""",
        slug="ride_review_inform_passenger",
        is_html=True)
    # TODO link!


def clean_cache(apps, schema_editor):
    from dbmail.models import MailTemplate, ApiKey

    MailTemplate.clean_cache()
    ApiKey.clean_cache()


class Migration(migrations.Migration):

    dependencies = [
        ('dbmail_templates', '0013_email_ride_review_inform_driver'),
    ]

    operations = [
        migrations.RunPython(load_mail_template),
        migrations.RunPython(clean_cache),
    ]
