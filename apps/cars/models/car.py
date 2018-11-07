from django.db import models


class Car(models.Model):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='cars')
    brand = models.CharField(
        max_length=50)
    model = models.CharField(
        max_length=50)
    number_of_seats = models.PositiveSmallIntegerField(
        verbose_name='Maximum number of seats in this car')
    color = models.CharField(
        max_length=50)
    license_plate = models.CharField(
        max_length=50,
        blank=True, null=True)
    production_year = models.IntegerField(
        blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return '{0} {1} - {2}'.format(
            self.brand,
            self.model,
            self.owner.get_public_name())
