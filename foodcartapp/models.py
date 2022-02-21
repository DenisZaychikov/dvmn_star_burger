from collections import defaultdict

from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from foodcartapp.geocoder import get_distance
from restaurateur.restaurants import is_available_restaurant


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )
    lat = models.FloatField('широта', null=True, blank=True)
    lon = models.FloatField('долгота', null=True, blank=True)

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
                .filter(availability=True)
                .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def with_total_prices(self):
        orders = self.annotate(common_price=Sum(
            F('details__fixed_price') * F('details__quantity'), output_field=DecimalField()))
        return orders

    def with_restaurants_in_orders(self):
        products_in_orders = {}
        for order in self:
            products_in_orders[order] = [detail.product for detail in order.details.all()]

        products_in_restaurants = defaultdict(list)
        restaurant_menu_items = RestaurantMenuItem.objects.filter(
            availability=True).prefetch_related('restaurant', 'product')
        for restaurant_menu_item in restaurant_menu_items:
            products_in_restaurants[restaurant_menu_item.restaurant].append(
                restaurant_menu_item.product)

        restaurants_in_orders = defaultdict(list)
        for order, order_products in products_in_orders.items():
            for restaurant, restaurant_products in products_in_restaurants.items():
                if is_available_restaurant(order_products, restaurant_products):
                    restaurants_in_orders[order].append(restaurant)
        restaurants_in_orders = dict(restaurants_in_orders)
        for order, restaurants in restaurants_in_orders.items():
            restaurants_with_distances = []
            for restaurant in restaurants:
                distance = get_distance(restaurant, order)
                restaurant_with_distance = f'{restaurant} - {distance} км.'
                restaurants_with_distances.append(restaurant_with_distance)
            order.restaurants = restaurants_with_distances
        return self


class Order(models.Model):
    CASH = 'cash'
    CREDITCARD = 'creditcard'
    UNSPECIFIED = 'unspecified'
    PROCESSED = 'processed'
    UNPROCESSED = 'unprocessed'
    PAYMENT_METHOD = [
        (UNSPECIFIED, 'не указано'),
        (CASH, 'наличностью'),
        (CREDITCARD, 'электронно')

    ]
    ORDER_STATUS = [
        (PROCESSED, 'обработанный'),
        (UNPROCESSED, 'необработанный')
    ]

    firstname = models.CharField('имя', max_length=20)
    lastname = models.CharField('фамилия', max_length=20)
    address = models.CharField('адрес', max_length=100)
    phonenumber = PhoneNumberField('телефон', db_index=True)
    comment = models.TextField('комментарий', blank=True)
    lat = models.FloatField('широта', null=True, blank=True)
    lon = models.FloatField('долгота', null=True, blank=True)
    restaurant = models.ForeignKey(
        Restaurant,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='ресторан',
        on_delete=models.CASCADE
    )
    registered_at = models.DateTimeField(
        'зарегистрирован в',
        default=timezone.now,
        db_index=True
    )
    called_at = models.DateTimeField(
        'позвонили в',
        null=True,
        blank=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        'доставлен в',
        null=True,
        blank=True,
        db_index=True
    )
    payment_method = models.CharField(
        'способ оплаты',
        max_length=20,
        choices=PAYMENT_METHOD,
        default=UNSPECIFIED,
        db_index=True
    )
    status = models.CharField(
        'статус',
        max_length=20,
        choices=ORDER_STATUS,
        default=UNPROCESSED,
        db_index=True
    )
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderDetails(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='details',
                              verbose_name='заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='details',
                                verbose_name='продукт')
    quantity = models.IntegerField(
        'количество',
        validators=[MinValueValidator(1)]
    )
    fixed_price = models.DecimalField(
        'фиксированная цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'детали заказа'
        verbose_name_plural = 'детали заказов'

    def __str__(self):
        return f'{self.order.firstname} {self.product.name}'
