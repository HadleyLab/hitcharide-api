from django.db import models


class FlatPage(models.Model):
    slug = models.CharField(
        primary_key=True,
        unique=True,
        max_length=80)
    content = models.TextField()

    def __str__(self):
        return self.slug
