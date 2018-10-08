from apps.main.utils import generate_filename


def user_photo_path(instance, filename):
    new_filename = generate_filename(filename)

    return '/'.join([
        'users', str(instance.pk),
        'avatars', new_filename,
    ])
