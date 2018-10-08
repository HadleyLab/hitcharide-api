from apps.main.utils import generate_filename


def car_photo_path(instance, filename):
    car = instance.car
    user = car.owner

    new_filename = generate_filename(filename)

    return '/'.join([
        'users', str(user.pk),
        'cars', str(car.pk),
        'images', new_filename,
    ])
