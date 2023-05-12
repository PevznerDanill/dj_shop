from django.http import HttpRequest, QueryDict
from .basket import Basket
from app_users.models import Profile
from app_goods.models import Product, Order, Item
from decimal import Decimal
from typing import List


def process_request(request: HttpRequest) -> str:
    """
    Takes the data from the POST request and passes it to the basket object to perform
    called methods.
    Returns the anchor to be link in the next get response.
    """
    basket = Basket(request)
    query_dict = request.POST
    action = query_dict.__getitem__('action')
    item_id = query_dict.__getitem__('item_id')

    if action == 'increase':
        basket.add_product(item_id)
    elif action == 'decrease':
        basket.decrease_amount(item_id)
    elif action == 'remove':
        basket.delete_product(item_id)

    return query_dict.__getitem__('anchor')


def take_products_from_shops(basket: Basket) -> List[Product]:
    """
    Takes the items from the basket, edites its quantity and ordered_quantity attributes.
    Returns a list of the items.
    """
    items_taken = []
    for item in basket:
        cur_item = item['item']
        amount = item['amount']
        cur_item.quantity -= amount
        cur_item.update_available()
        cur_item.ordered_quantity += amount
        items_taken.append(cur_item)
    Item.objects.bulk_update(items_taken, ['quantity', 'available', 'ordered_quantity'])
    basket.clear_basket()
    return items_taken


def create_order(products_taken: List[Product], address: str, profile: Profile, discount: str) -> int:
    """
    Creates a new order from the passed data and returns its id.
    """
    new_order = Order.objects.create(
        delivery_address=address,
        profile=profile
    )
    if discount != '':
        new_order.discount = int(discount)
    new_order.save()
    new_order.items.add(*products_taken)
    profile.update_status()
    profile.orders_count += 1
    profile.update_discount()
    profile.save()
    return new_order.pk


def spend_money(profile: Profile, basket: Basket, discount: str) -> Decimal:
    """
    Calculates the total price of the ordered items and subtracts it from the profile's balance.
    """
    total_sum = basket.total_sum()
    if discount != '':
        discount_to_use = Decimal(discount)
        total_sum -= total_sum / 100 * discount_to_use
        profile.use_discount(discount)
    profile.balance -= total_sum
    profile.save(update_fields=['balance'])
    return total_sum

