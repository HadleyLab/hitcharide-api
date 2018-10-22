from django.db import models
from ckeditor.fields import RichTextField


class FlatPage(models.Model):
    slug = models.CharField(
        primary_key=True,
        unique=True,
        max_length=80)
    content = RichTextField()

    def __str__(self):
        return self.slug
