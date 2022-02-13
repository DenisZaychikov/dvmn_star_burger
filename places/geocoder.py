import requests
from geopy import distance

from places.models import RestaurantGeoPosition


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


def get_distance(restaurant, order, geopy_token, restaurants_geopos):
    lat, lon = None, None
    order_coords = order.lat, order.lon
    for restaurant_geopos in restaurants_geopos:
        if restaurant.address == restaurant_geopos.address:
            restaurant_coords = restaurant_geopos.lat, restaurant_geopos.lon
            return None, round(distance.distance(order_coords, restaurant_coords).km, 2)
    coords = fetch_coordinates(geopy_token, restaurant.address)
    if coords:
        lat, lon = coords
    restaurant_geopos = RestaurantGeoPosition.objects.create(
        address=restaurant.address,
        lat=lat,
        lon=lon
        )

    restaurant_coords = restaurant_geopos.lat, restaurant_geopos.lon
    return restaurant_geopos, round(distance.distance(order_coords, restaurant_coords).km, 2)
