import paypalrestsdk


def inform_all_subscribers(ride):
    ride.stops.all().values_list('city_id').exclude()


def ride_booking_paypal_payment(ride_booking):
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
                    "price": "{0}".format(ride_booking.ride.price_with_fee),
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "{0}".format(ride_booking.ride.price_with_fee),
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
      print("Payment created successfully")
    else:
      print(payment.error)
