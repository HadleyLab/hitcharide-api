from .models import RideRequest


def inform_all_subscribers(ride):
    ride.stops.all().values_list('city_id').exclude()
