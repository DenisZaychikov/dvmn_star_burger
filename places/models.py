from django.db import models
from django.utils import timezone


class RestaurantGeoPosition(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
    )
    lat = models.FloatField('широта', null=True, blank=True)
    lon = models.FloatField('долгота', null=True, blank=True)
    request_date = models.DateTimeField('Дата запроса к геокодеру',
                                        default=timezone.now)

    class Meta:
        verbose_name = 'геопозиция ресторана'
        verbose_name_plural = 'геопозиция ресторанов'

    def __str__(self):
        return self.address
