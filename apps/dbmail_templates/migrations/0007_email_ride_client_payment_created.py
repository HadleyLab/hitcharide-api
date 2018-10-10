# Generated by Django 2.1 on 2018-09-24 04:54
from dbmail.models import MailTemplate
from django.db import migrations


def load_mail_template(apps, schema_editor):
    MailTemplate.objects.create(
        name="The payment for the ride has been created",
        subject="The payment for the ride {{ booking.ride }} has been created",
        message="""
        <p>You're receiving this email because you need to pay for booked ride.</p>
        <p>You can pay by this link: <a href={{ booking.paypal_approval_link }}></a>
        <p><b>There is an information about the ride:<b><br>
        <b>Car:</b> {{ booking.ride.car }}<br>
        <b>Number of sits:</b> {{ booking.ride.number_of_seats }}<br>
        <b>Description:</b> {{ booking.ride.description }}<br
        </p>
        <p>Thanks for using our site!</p>
        <p>The {{ site_name }} team</p>""",
        slug="ride_client_payment_created",
        is_html=True,)


def delete_mail_template(apps, schema_editor):
    MailTemplate.objects.filter(
        slug='ride_client_payment_created'
    ).delete()


def clean_cache(apps, schema_editor):
    from dbmail.models import MailTemplate, ApiKey

    MailTemplate.clean_cache()
    ApiKey.clean_cache()


class Migration(migrations.Migration):

    dependencies = [
        ('dbmail_templates', '0006_email_new_ride_complaint'),
    ]

    operations = [
        migrations.RunPython(load_mail_template, delete_mail_template),
        migrations.RunPython(clean_cache, lambda apps, schema_editor: None),
    ]
