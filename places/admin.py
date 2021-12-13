from django.contrib import admin

from places.models import RestaurantGeoPosition


@admin.register(RestaurantGeoPosition)
class RestaurantGeoPositionAdmin(admin.ModelAdmin):
    pass

