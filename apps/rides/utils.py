from django.conf import settings
from django.db import transaction
from django.urls import reverse
from paypalrestsdk import Payment, Payout, Sale

from apps.main.utils import send_mail
from apps.rides.models import RideBookingStatus, Ride, RideBooking, RideStatus


def inform_all_subscribers(ride):
    ride.stops.all().values_list('city_id').exclude()


def ride_booking_create_payment(ride_booking, request):
    ride_total = ride_booking.ride.price_with_fee * ride_booking.seats_count
    ride_detail_url = settings.RIDE_DETAIL_URL.format(
        ride_pk=ride_booking.ride.pk)
    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url":
                request.build_absolute_uri(
                    reverse('ridebooking-paypal-payment-execute',
                            kwargs={'pk': ride_booking.pk})),
            "cancel_url": ride_detail_url},
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
            "description":
                "This is the payment transaction for the ride booking."}]})

    if not payment.create():
        raise Exception("Cannot create a payment:\n{0}".format(payment.error))

    approval_link = [
        link['href'] for link in payment.links
        if link['rel'] == 'approval_url'][0]
    ride_booking.paypal_payment_id = payment.id
    ride_booking.paypal_approval_link = approval_link
    ride_booking.save()
    send_mail('ride_client_payment_created',
              [ride_booking.client.email],
              {'booking': ride_booking})


def ride_payout(ride):
    total_for_driver = ride.total_for_driver
    if not total_for_driver:
        return

    payout = Payout({
        "sender_batch_header": {
            "sender_batch_id": "{0}_ride_{1}".format(
                settings.PAYPAL_BATCH_PREFIX,
                ride.pk),
            "email_subject": "You have a payout"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "amount": {
                    "value": '{0:.2f}'.format(total_for_driver),
                    "currency": "USD"
                },
                "receiver": ride.car.owner.paypal_account,
                "note": "The payout for the ride {0}. Thank you.".format(
                    ride
                ),
                "sender_item_id": "ride_{0}".format(ride.pk)
            }
        ]
    })

    if not payout.create():
        raise Exception("Cannot create a payout:\n{0}".format(payout.error))

    send_mail('ride_payout_to_owner',
              [ride.car.owner.email],
              {'ride': ride})


def ride_booking_refund(ride_booking):
    refund_total = ride_booking.ride.price_with_fee * \
                   ride_booking.seats_count
    payment = Payment.find(ride_booking.paypal_payment_id)
    sale_id = payment.transactions[0].related_resources[0]['sale'].id
    sale = Sale.find(sale_id)

    refund = sale.refund({
        "amount": {
            "total": '{0:.2f}'.format(refund_total),
            "currency": "USD"}})

    if not refund.success():
        raise Exception("Cannot create a refund:\n{0}".format(refund.error))

@transaction.atomic
def cancel_ride_by_driver(ride):
    ride_bookings = ride.bookings.filter(status__in=RideBookingStatus.ACTUAL)
    for booking in ride_bookings:
        if booking.status == RideBookingStatus.PAYED:
            ride_booking_refund(booking)
            send_mail('ride_has_been_deleted',
                      [booking.client.email],
                      {'ride': ride})

        if booking.status == RideBookingStatus.CREATED:
            send_mail('ride_has_been_deleted',
                      [booking.client.email],
                      {'ride': ride})
        booking.status = RideBookingStatus.REVOKED
        booking.save()
    ride.status = RideStatus.CANCELED
    ride.save()

def ride_booking_execute_payment(payer_id, ride_booking):
    payment = Payment.find(ride_booking.paypal_payment_id)

    if ride_booking.status == RideBookingStatus.CREATED:
        if payment.execute({"payer_id": payer_id}):
            ride_booking.status = RideBookingStatus.PAYED
            ride_booking.save()
            send_mail('ride_client_payment_executed',
                      [ride_booking.client.email],
                      {'ride': ride_booking})
            send_mail('ride_owner_payment_executed',
                      [ride_booking.ride.car.owner.email],
                      {'ride': ride_booking})

            return True

    return False
