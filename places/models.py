from django.db import models
from django.utils import timezone


class RestaurantGeoPosition(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
        unique=True
    )
    address = models.CharField(
        'адрес',
        max_length=100,
    )
    lat = models.FloatField('широта')
    lon = models.FloatField('долгота')
    request_date = models.DateTimeField('Дата запроса к геокодеру',
                                        default=timezone.now)

    class Meta:
        verbose_name = 'геопозиция ресторана'
        verbose_name_plural = 'геопозиция ресторанов'

    def __str__(self):
        return self.name
