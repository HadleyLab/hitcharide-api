from django.db import models


class State(models.Model):
    name = models.CharField(
        max_length=50)

    def __str__(self):
        return self.name


class City(models.Model):
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='cities')
    name = models.CharField(
        max_length=50)

    def __str__(self):
        return '{0}, {1}'.format(self.name, self.state.name)
