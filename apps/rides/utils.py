import logging

import paypalrestsdk


logger = logging.getLogger()


def inform_all_subscribers(ride):
    ride.stops.all().values_list('city_id').exclude()


def ride_booking_paypal_payment(ride_booking):
    ride_total = ride_booking.ride.price_with_fee
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",
            "cancel_url": "http://localhost:3000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "ride_booking",
                    "sku": "{0}".format(ride_booking.pk),
                    "price": "{0}".format(ride_total),
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "{0}".format(ride_total),
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        logger.error("HELLO IM HERE")
        ride_booking.paypal_payment_id = payment.id
        ride_booking.save()
    else:
        print(payment.error)
