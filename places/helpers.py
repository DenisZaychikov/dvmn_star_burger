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


def save_restaurant(lat, lon, restaurant):
    restaurant = RestaurantGeoPosition.objects.create(
        address=restaurant.address,
        lat=lat,
        lon=lon
    )
    return restaurant


def get_distance(restaurant, order, geopy_token):
    lat, lon = None, None
    try:
        restaurant_geopos = RestaurantGeoPosition.objects.get(address=restaurant.address)
    except RestaurantGeoPosition.DoesNotExist:
        coords = fetch_coordinates(geopy_token, restaurant.address)
        if coords is not None:
            lat, lon = coords[0], coords[1]
        restaurant_geopos = save_restaurant(lat, lon, restaurant)

    order_coords = (order.lat, order.lon)
    restaurant_coords = (restaurant_geopos.lat, restaurant_geopos.lon)
    return round(distance.distance(order_coords, restaurant_coords).km, 2)


def is_available_restaurant(order_products, restaurant_products):
    return all(product in restaurant_products for product in order_products)
