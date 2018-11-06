from django.core.management.base import BaseCommand
from dbmail.models import MailTemplate, MailBaseTemplate


class Command(BaseCommand):
    help = "Initialize dbmail templates"

    def create_email_templates(self):
        MailTemplate.objects.create(
            name="Account activate",
            subject="{{ site_name }} | Account activation",
            message="""
            <p>You're receiving this email because you need to finish activation process on {{ site_name }}.</p>
            <p>Please go to the following page to activate account:</p>
            <p><a href="{{ url|safe }}">{{ url|safe }}</a></p>
            <p>Thanks for using our site!</p>
            <p>The {{ site_name }} team</p>""",
            slug="email_user_account_activation",
            is_html=True
        )

        MailTemplate.objects.create(
            name="Account confirmation",
            subject="{{ site_name }} | Your account has been successfully created and activated!",
            message="""
            <p>Your account has been created and is ready to use!</p>
            <p>Thanks for using our site!</p>
            <p>The {{ site_name }} team</p>""",
            slug="email_user_account_confirmation",
            is_html=True
        )

        MailTemplate.objects.create(
            name="Password reset",
            subject="{{ site_name }} | Password reset",
            message="""
            <p>You're receiving this email because you requested a password reset for your user account at {{ site_name }}.</p>
            <p>Please go to the following page and choose a new password:</p>
            <a href="{{ url|safe }}">{{ url|safe }}</a>
            <p>Your username, in case you've forgotten: <b>{{ user.get_username }}</b></p>
            <p>Thanks for using our site!</p>
            <p>The {{ site_name }} team</p>""",
            slug="email_user_account_password_reset",
            is_html=True
        )

        MailTemplate.objects.create(
            name="The ride has been canceled (to passenger)",
            subject="{{ site_name }} | The ride {{ ride }} has been deleted",
            message="""
            <p>You're receiving this email because your booked ride has been deleted at {{ site_name }}.</p>
            <p>Thanks for using our site!</p>
            <p>The {{ site_name }} team</p>""",
            slug="email_passenger_ride_canceled",
            is_html=True
        )

        MailTemplate.objects.create(
            name="The ride has the new complaint (to manager)",
            subject="{{ site_name }} | The {{ complaint.ride }} has the new complaint",
            message="""
            <p>Complaint body:</p>
            <p>{{ complaint.description }}</p>
            <p><b>Passenger info:</b><br>
            <b>Full name:</b> {{ complaint.user.get_full_name }}<br>
            <b>Phone:</b> +{{ complaint.user.phone }}<br>
            <b>Email:</b> {{ complaint.user.email }}<br>
            
            <p><b>There is an information about the ride:<b><br>
            <b>Car:</b> {{ complaint.ride.car }}<br>
            <b>Driver full name:</b> {{ complaint.ride.car.owner.get_full_name }}<br>
            <b>Driver phone:</b> +{{ complaint.ride.car.owner.phone }}<br>
            <b>Driver email:</b> {{ complaint.ride.car.owner.email }}<br>
            <b>Number of seats:</b> {{ complaint.ride.number_of_seats }}<br>
            <b>Description:</b> {{ complaint.ride.description }}<br>
            </p>,
            <p>You can see the ride details <a href='{{ ride_detail|safe }}'>here</a></p>
            <p>Also you can see the complaint details in <a href='{{ backend_url}}/admin/rides/ridecomplaint/{{ complaint.pk }}/'>admin interface</a></p>
            """,
            slug="email_manager_ride_complaint_created",
            is_html=True
        )

        MailTemplate.objects.create(
            name="The ride booking has been created (to passenger)",
            subject="{{ site_name }} | The payment for the ride {{ booking.ride }} has been created",
            message="""
            <p>You're receiving this email because you need to pay for a booked ride.</p>
            <p>You can pay by this link: <a href='{{ booking.paypal_approval_link|safe }}'>{{ booking.paypal_approval_link|safe }}</a>
            <p><b>There is an information about the ride:<b><br>
            <b>Car:</b> {{ booking.ride.car }}<br>
            <b>Number of seats:</b> {{ booking.ride.number_of_seats }}<br>
            <b>Description:</b> {{ booking.ride.description }}<br
            </p>
            <p>
            The Cost Contribution for the ride includes<br>
            Driver reward: {{ booking.ride.price }} $
            Service fee: {{ booking.ride.fee_price }} $
            </p>
            <p>You can see the ride details <a href='{{ ride_detail|safe }}'>here</a></p>
            <p>Thanks for using our site!</p>
            <p>The {{ site_name }} team</p>""",
            slug="email_passenger_ride_booking_created",
            is_html=True
        )

        MailTemplate.objects.create(
            name="New ride for ride request (to passenger)",
            subject="{{ site_name }} | You have a new ride suggest: {{ ride }}",
            message="""
            <p>You created a ride request {{ ride_request }}</p>
            <p>There is a ride for you:</p>
            <p>You can see the ride details <a href='{{ ride_detail|safe }}'>here</a></p>
            """,
            slug="email_passenger_ride_request_ride_suggest",
            is_html=True
        )

        MailTemplate.objects.create(
            name="The payment for the ride has been executed (to driver)",
            subject="{{ site_name }} | The payment for the ride {{ ride }} has been executed",
            message="""
            <p>You're receiving this email because we have the payment for the your ride</p>
            <p><b>There is an information about the ride:<b><br>
            <b>Car:</b> {{ ride.car }}<br>
            <b>Number of seats:</b> {{ ride.number_of_seats }}<br>
            <b>Description:</b> {{ ride.description }}<br
            </p>
            <p>
            The Cost Contribution for the ride includes<br>
            Driver reward: {{ ride.price }} $
            Service fee: {{ ride.fee_price }} $
            </p>
            <p>You can see the ride details <a href='{{ ride_detail|safe }}'>here</a></p>
            <p>Thanks for using our site!</p>
            <p>The {{ site_name }} team</p>""",
            slug="email_driver_ride_booking_payed",
            is_html=True
        )

        MailTemplate.objects.create(
            name="The payment for the ride has been executed (to passenger)",
            subject="{{ site_name }} | The payment for the ride {{ ride }} has been executed",
            message="""
            <p>You're receiving this email because your payment for the ride has been executed</p>
            <p><b>There is an information about the ride:<b><br>
            <b>Car:</b> {{ ride.car }}<br>
            <b>Number of seats:</b> {{ ride.number_of_seats }}<br>
            <b>Description:</b> {{ ride.description }}<br>
            </p>
            <p>
            The Cost Contribution for the ride includes<br>
            Driver reward: {{ ride.price }} $
            Service fee: {{ ride.fee_price }} $
            </p>
            <p>You can see the ride details <a href='{{ ride_detail|safe }}'>here</a></p>
            <p>Thanks for using our site!</p>
            <p>The {{ site_name }} team</p>""",
            slug="email_passenger_ride_booking_payed",
            is_html=True
        )

        MailTemplate.objects.create(
            name="The payout for the ride (to driver)",
            subject="{{ site_name }} | You have a payout for the ride {{ ride }}.",
            message="""
            <p>You're receiving this email because you have a payout for the ride.</p>
            <p><b>There is an information about the ride:<b><br>
            <b>Car:</b> {{ ride.car }}<br>
            <b>Number of seats:</b> {{ ride.number_of_seats }}<br>
            <b>Description:</b> {{ ride.description }}<br
            </p>
            <p>
            Your reward: {{ ride.total_for_driver }} $
            </p>
            <p>You can see the ride details <a href='{{ ride_detail|safe }}'>here</a></p>
            <p>Thanks for using our site!</p>
            <p>The {{ site_name }} team</p>""",
            slug="email_driver_ride_payout",
            is_html=True
        )

        MailTemplate.objects.create(
            name="The ride booking canceled (to passenger)",
            subject="{{ site_name }} | Information about canceled ride {{ ride }}.",
            message="""
            <p>You're receiving this email because you canceled the ride booking</p>
            <p><b>There is an information about the ride:<b><br>
            <b>Car:</b> {{ ride.car }}<br>
            <b>Number of seats:</b> {{ ride.number_of_seats }}<br>
            <b>Description:</b> {{ ride.description }}<br>
            </p>
            <p>You can see the ride details <a href='{{ ride_detail|safe }}'>here</a></p>
            <p>You payment will be refunded soon by PayPal.</p>
            <p>Thanks for using our site!</p>
            <p>The {{ site_name }} team</p>""",
            slug="email_passenger_ride_booking_canceled",
            is_html=True
        )

        MailTemplate.objects.create(
            name="The ride booking canceled (to driver)",
            subject="{{ site_name }} | The client canceled the booking for ride {{ ride }}",
            message="""
            <p>You're receiving this email because the client canceled the ride booking</p>
            <p><b>There is an information about the ride:<b><br>
            <b>Car:</b> {{ ride.car }}<br>
            <b>Number of seats:</b> {{ ride.number_of_seats }}<br>
            <b>Description:</b> {{ ride.description }}<br>
            </p>
            <p>You can see the ride details <a href='{{ ride_detail|safe }}'>here</a></p>
            <p>Thanks for using our site!</p>
            <p>The {{ site_name }} team</p>""",
            slug="email_driver_ride_booking_canceled",
            is_html=True
        )

        MailTemplate.objects.create(
            name="Rate the ride passengers (to driver)",
            subject="{{ site_name }} | You can rate passengers from the ride {{ ride }}",
            message="""
            <p></p>
            <p>You can rate passengers from your ride, 
            by using this link: <a href='{{ review_url|safe }}'>rate passengers.</a>
            </p>
            <p>Thanks for using our site!</p>
            <p>The {{ site_name }} team</p>""",
            slug="email_driver_rate_passengers",
            is_html=True
        )

        MailTemplate.objects.create(
            name="Rate the ride (to passenger)",
            subject="{{ site_name }} | You can rate the ride {{ ride }}",
            message="""
                <p></p>
                <p>You can rate the ride {{ ride }} and driver 
                {{ driver.first_name }} {{ driver.last_name }}<br>
                <b>Date:</b> {{ ride_date_time }}<br>
                <b>Car:</b> {{ ride.car }}<br>
                <b>Number of seats:</b> {{ ride.number_of_seats }}<br>
                <b>Description:</b> {{ ride.description }}<br>
                Using this link: <a href='{{ review_url|safe }}'>rate a ride.</a>
                </p>
                <p>Thanks for using our site!</p>
                <p>The {{ site_name }} team</p>""",
            slug="email_passenger_rate_driver",
            is_html=True
        )

    def create_sms_templates(self):
        MailTemplate.objects.create(
            name="SMS Phone validation",
            message="Your Hitcharide activation code is {{ code }}",
            slug="sms_user_phone_validation",
            is_html=False
        )

        MailTemplate.objects.create(
            name="SMS Ride has been canceled (to passenger)",
            message="Ride {{ ride }} has been canceled by a driver",
            slug="sms_passenger_ride_canceled",
            is_html=False
        )

        MailTemplate.objects.create(
            name="SMS New ride for ride request (to passenger)",
            message="You have a new ride suggest: {{ ride }}. "
                    "{{ ride_detail|safe }}",
            slug="sms_passenger_ride_request_ride_suggest",
            is_html=False
        )

        MailTemplate.objects.create(
            name="SMS Ride booking canceled (to driver)",
            message="The client cancelled a payed booking for ride {{ ride }}. "
                    "{{ ride_detail|safe }}",
            slug="sms_driver_ride_booking_canceled",
            is_html=False
        )

        MailTemplate.objects.create(
            name="SMS Ride booking payed (to driver)",
            message="You have a new payed ride booking for ride {{ ride }}. "
                    "{{ ride_detail|safe }}",
            slug="sms_driver_ride_booking_payed",
            is_html=False
        )

        MailTemplate.objects.create(
            name="SMS Ride payout (to driver)",
            message="You have a payout for ride {{ ride }}. "
                    "{{ ride_detail|safe }}",
            slug="sms_driver_ride_payout",
            is_html=False
        )

    def handle(self, **options):
        MailTemplate.objects.all().delete()

        self.create_email_templates()
        self.create_sms_templates()
