def is_available_restaurant(order_products, restaurant_products):
    return all(product in restaurant_products for product in order_products)
