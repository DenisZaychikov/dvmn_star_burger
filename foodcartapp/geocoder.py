import requests
from geopy import distance


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


def get_distance(restaurant, order):
    if not order.lat or restaurant.lat:
        return 'расстояние не определено'
    order_coords = order.lat, order.lon
    restaurant_coords = restaurant.lat, restaurant.lon
    return round(distance.distance(order_coords, restaurant_coords).km, 2)
