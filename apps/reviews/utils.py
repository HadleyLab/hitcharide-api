from django.db.models import Avg, Count


def calc_rating(reviews_qs):
    result = reviews_qs.aggregate(
        rating=Avg('rating'),
        count=Count('pk'))
    return {
        'value': result['rating'] or 0.0,
        'count': result['count']
    }
