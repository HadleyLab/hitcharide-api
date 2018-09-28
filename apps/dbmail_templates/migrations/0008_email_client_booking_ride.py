# Generated by Django 2.1 on 2018-09-28 08:38
from dbmail.models import MailTemplate
from django.db import migrations


def load_mail_template(apps, schema_editor):
    MailTemplate.objects.create(
        name="Client booked a ride",
        subject="You booked a ride {{ ride }}",
        message="""
        <p>You're receiving this email because you booked a ride at {{ site_name }}.</p>
        <p><b>There is an information about the ride:<b><br>
        <b>Car:</b> {{ ride.car }}<br>
        <b>Number of sits:</b> {{ ride.number_of_sits }}<br>
        <b>Description:</b> {{ ride.description }}<br
        </p>
        <p>Thanks for using our site!</p>
        <p>The {{ site_name }} team</p>""",
        slug="client_booked_a_ride",
        is_html=True,)


def clean_cache(apps, schema_editor):
    from dbmail.models import MailTemplate, ApiKey

    MailTemplate.clean_cache()
    ApiKey.clean_cache()



class Migration(migrations.Migration):

    dependencies = [
        ('dbmail_templates', '0007_email_ride_request_new_offer'),
    ]

    operations = [
        migrations.RunPython(load_mail_template),
        migrations.RunPython(clean_cache),
    ]
