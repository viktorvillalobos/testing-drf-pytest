from time import strptime

from django.db import models


class CarManager(models.Manager):

    def get_cars_by_created(self, my_date):
        date = strptime(my_date, '%Y-%m-%d')
        queryset = self.get_queryset()
        return queryset.filter(created__year=date.tm_year,
                               created__month=date.tm_mon,
                               created__day=date.tm_mday)
