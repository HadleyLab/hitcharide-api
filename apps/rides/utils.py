import logging

from dbmail import send_db_mail
from django.urls import reverse
from paypalrestsdk import Payment, Payout, ResourceNotFound


logger = logging.getLogger()


def inform_all_subscribers(ride):
    ride.stops.all().values_list('city_id').exclude()

def ride_booking_paypal_payment(request, ride_booking):
    ride_total = ride_booking.ride.price_with_fee * ride_booking.seats_count
    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url":
                request.build_absolute_uri(
                    reverse('ridebooking-paypal-payment-execute',
                            kwargs={'pk': ride_booking.pk})),
            "cancel_url": "http://localhost:3000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "ride_booking",
                    "sku": "{0}".format(ride_booking.pk),
                    "price": '{0:.2f}'.format(ride_total),
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": '{0:.2f}'.format(ride_total),
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        logger.error(payment.links)
        approval_link = [
            link['href'] for link in payment.links
            if link['rel'] == 'approval_url'][0]
        logger.error(approval_link)
        ride_booking.paypal_payment_id = payment.id
        ride_booking.paypal_approval_link = approval_link
        ride_booking.save()
        send_db_mail('ride_client_payment_created',
                     [ride_booking.client.email],
                     {'booking': ride_booking})
    else:
        logger.error(payment.error)


def ride_payout(ride):
    payout = Payout({
        "sender_batch_header": {
            "sender_batch_id": "ride_{0}".format(ride.pk),
            "email_subject": "You have a payment"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "amount": {
                    "value": '{0:.2f}'.format(ride.total_for_driver),
                    "currency": "USD"
                },
                "receiver": ride.car.owner.paypal_account,
                "note": "Thank you.",
                "sender_item_id": "ride_{0}".format(ride.pk)
            }
        ]
    })

    if payout.create():
        print("payout[%s] created successfully" %
              (payout.batch_header.payout_batch_id))
    else:
        print(payout.error)
