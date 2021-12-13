import requests
from django.core.management.base import BaseCommand
from places.models import RestaurantGeoPosition
from star_burger.settings import GEOPY_TOKEN


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection'][
        'featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


class Command(BaseCommand):
    help = 'New retaurant geoposition'

    def add_arguments(self, parser):
        parser.add_argument('restaurant', nargs='+', type=str)

    def handle(self, *args, **options):
        restaurant_name, restaurant_address = options['restaurant']
        coords = fetch_coordinates(GEOPY_TOKEN, restaurant_address)
        print(coords)
        # restaurant_lat, restaurant_lon = fetch_coordinates(GEOPY_TOKEN, restaurant_address)
        # restaurant = RestaurantGeoPosition.objects.create(
        #     name=restaurant_name,
        #     address=restaurant_address,
        #     lat=restaurant_lat,
        #     lon=restaurant_lon
        # )
