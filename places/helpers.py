import requests
from django.http import Http404
from django.shortcuts import get_object_or_404
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


def save_restaurant(restaurant, geopy_token):
    restaurant_lat, restaurant_lon = fetch_coordinates(
        geopy_token,
        restaurant.address
    )
    restaurant = RestaurantGeoPosition.objects.create(
        name=restaurant.name,
        address=restaurant.address,
        lat=restaurant_lat,
        lon=restaurant_lon
    )
    return restaurant


def get_distance(restaurant, order, geopy_token):
    try:
        restaurant_geopos = get_object_or_404(
            RestaurantGeoPosition,
            name=restaurant.name,
        )
    except Http404:
        restaurant_geopos = save_restaurant(restaurant, geopy_token)

    order_coords = fetch_coordinates(geopy_token, order.address)
    restaurant_coords = (restaurant_geopos.lat, restaurant_geopos.lon)
    return round(distance.distance(order_coords, restaurant_coords).km, 2)


def is_available_restaurant(order_products, restaurant_products):
    for product in order_products:
        if product in restaurant_products:
            continue
        else:
            return False
    return True
