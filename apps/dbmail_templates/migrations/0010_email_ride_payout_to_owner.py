# Generated by Django 2.1 on 2018-09-24 05:07
from dbmail.models import MailTemplate
from django.db import migrations


def load_mail_template(apps, schema_editor):
    MailTemplate.objects.create(
        name="The payout for the ride (to owner)",
        subject="You have a payout for the ride {{ ride }}.",
        message="""
        <p>You're receiving this email because you have a payout for the ride.</p>
        <p><b>There is an information about the ride:<b><br>
        <b>Car:</b> {{ ride.car }}<br>
        <b>Number of sits:</b> {{ ride.number_of_seats }}<br>
        <b>Description:</b> {{ ride.description }}<br
        </p>
        <p>Thanks for using our site!</p>
        <p>The {{ site_name }} team</p>""",
        slug="ride_payout_to_owner",
        is_html=True,)


def delete_mail_template(apps, schema_editor):
    MailTemplate.objects.filter(
        slug='ride_payout_to_owner'
    ).delete()


def clean_cache(apps, schema_editor):
    from dbmail.models import MailTemplate, ApiKey

    MailTemplate.clean_cache()
    ApiKey.clean_cache()


class Migration(migrations.Migration):

    dependencies = [
        ('dbmail_templates', '0009_email_ride_owner_payment_has_been_executed'),
    ]

    operations = [
        migrations.RunPython(load_mail_template, delete_mail_template),
        migrations.RunPython(clean_cache, lambda apps, schema_editor: None),
    ]
