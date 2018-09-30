from dbmail import send_db_mail
from django.urls import reverse
from django_extensions import settings
from paypalrestsdk import Payment, Payout, Sale

from apps.rides.models import RideBookingStatus


def inform_all_subscribers(ride):
    ride.stops.all().values_list('city_id').exclude()

def ride_booking_create_payment(ride_booking, request):
    ride_total = ride_booking.ride.price_with_fee * ride_booking.seats_count
    ride_booking_detail_url = settings.RIDE_BOOKING_DETAIL_URL.format(
        ride_pk=ride_booking.ride.pk, ride_booking_pk=ride_booking.pk)
    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url":
                request.build_absolute_uri(
                    reverse('ridebooking-paypal-payment-execute',
                            kwargs={'pk': ride_booking.pk})),
            "cancel_url": ride_booking_detail_url},
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

    if payment.create():
        approval_link = [
            link['href'] for link in payment.links
            if link['rel'] == 'approval_url'][0]
        ride_booking.paypal_payment_id = payment.id
        ride_booking.paypal_approval_link = approval_link
        ride_booking.save()
        send_db_mail('ride_client_payment_created',
                     [ride_booking.client.email],
                     {'booking': ride_booking})
        return True

    return False


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
                "note": "The payment for the ride {0}. Thank you.".format(
                    ride
                ),
                "sender_item_id": "ride_{0}".format(ride.pk)
            }
        ]
    })

    if payout.create():
        send_db_mail('ride_payout_to_owner',
                     [ride.car.owner.email],
                     {'ride': ride})
        return True

    return False


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

    if refund.success():
        ride_booking.status = RideBookingStatus.REFUNDED
        send_db_mail('client_ride_booking_canceled',
                     [ride_booking.client.email],
                     {'ride_booking': ride_booking})
        send_db_mail('owner_ride_booking_canceled',
                     [ride_booking.ride.owner.email],
                     {'ride_booking': ride_booking})
        return True

    return False


def ride_booking_execute_payment(payer_id, ride_booking):
    payment = Payment.find(ride_booking.paypal_payment_id)

    if ride_booking.status == RideBookingStatus.CREATED:
        if payment.execute({"payer_id": payer_id}):
            ride_booking.status = RideBookingStatus.PAYED
            ride_booking.save()
            send_db_mail('ride_client_payment_executed',
                         [ride_booking.client.email],
                         {'ride': ride_booking})
            send_db_mail('ride_owner_payment_executed',
                         [ride_booking.ride.owner.email],
                         {'ride': ride_booking})

            return True

    return False
