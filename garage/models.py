from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
from garage.managers import CarManager


class Car(models.Model):
    """A car model"""
    code = models.CharField(_('code'), max_length=10)
    name = models.CharField(_('name'), max_length=50)
    year = models.IntegerField(_('Year'))

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = CarManager()

    def __str__(self):
        return self.code


