from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem

from places.helpers import get_distance, is_available_restaurant
from star_burger.settings import GEOPY_TOKEN


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:
        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in
               product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in
                                restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.order_total_price().filter(
        order_status='unprocessed_order').prefetch_related(
        'details_orders__product')
    products_in_orders = {}
    for order in orders:
        for details in order.details_orders.all():
            if not order in products_in_orders:
                products_in_orders[order] = [details.product]
            else:
                products_in_orders[order].append(details.product)

    products_in_restaurants = {}
    restaurant_menu_items = RestaurantMenuItem.objects.filter(
        availability=True).prefetch_related('restaurant', 'product')
    for restaurant_menu_item in restaurant_menu_items:
        if not restaurant_menu_item.restaurant in products_in_restaurants:
            products_in_restaurants[restaurant_menu_item.restaurant] = [
                restaurant_menu_item.product]
        else:
            products_in_restaurants[restaurant_menu_item.restaurant].append(
                restaurant_menu_item.product)

    restaurants_in_orders = {}
    for order, order_products in products_in_orders.items():
        for restaurant, restaurant_products in products_in_restaurants.items():
            if is_available_restaurant(order_products, restaurant_products):
                distance = get_distance(restaurant, order, GEOPY_TOKEN)
                restaurant = f'{restaurant} - {distance} км.'
                if not order in restaurants_in_orders:
                    restaurants_in_orders[order] = [restaurant]
                else:
                    restaurants_in_orders[order].append(restaurant)

    return render(request, template_name='order_items.html', context={
        'restaurants_in_orders': restaurants_in_orders
    })
