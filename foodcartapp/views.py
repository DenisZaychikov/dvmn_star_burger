from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

from foodcartapp.geocoder import fetch_coordinates
from django.conf import settings
# from star_burger.settings import GEOPY_TOKEN
from .models import Product, Order, OrderDetails
from .serializers import OrderSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    lat, lon = None, None
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    firstname = serializer.validated_data['firstname']
    lastname = serializer.validated_data['lastname']
    phonenumber = serializer.validated_data['phonenumber']
    address = serializer.validated_data['address']
    coords = fetch_coordinates(settings.GEOPY_TOKEN, address)
    if coords:
        lat, lon = coords
    new_order = Order.objects.create(
        firstname=firstname,
        lastname=lastname,
        phonenumber=phonenumber,
        address=address,
        lat=lat,
        lon=lon
    )
    order_details = serializer.validated_data['products']
    OrderDetails.objects.bulk_create([
        OrderDetails(
            product=order_detail['product'],
            quantity=order_detail['quantity'],
            order=new_order,
            fixed_price=order_detail['product'].price)
        for order_detail in order_details
    ])
    return Response(serializer.data)
