from rest_framework.serializers import ModelSerializer

from foodcartapp.models import Order, OrderDetails


class OrderDetailsSerializer(ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = ['quantity', 'product']


class OrderSerializer(ModelSerializer):
    products = OrderDetailsSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']
