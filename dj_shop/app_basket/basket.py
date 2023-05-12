import copy
from django.http import HttpRequest
from app_goods.models import Item
from django.conf import settings
from decimal import Decimal


class Basket(object):
    """
    Describes the Basket object that is being initiated and stored in session.
    """
    def __init__(self, request: HttpRequest) -> None:
        """
        If not found in session, creates a key and a dictionary for the basket data.
        """
        self.session = request.session
        basket = self.session.get(settings.BASKET_SESSION_ID)

        if not basket:
            self.session[settings.BASKET_SESSION_ID] = {}

        self.basket = basket

    def save_session(self) -> None:
        """
        Saves current basket data in the session.
        """
        self.session[settings.BASKET_SESSION_ID] = self.basket
        self.session.modified = True

    def add_product(self, item_pk: str) -> None:
        """
        Retrieves Item instance by its id, gets its price, shop title and saves it in the
        basket data using the id as key..
        Also saves the amount of the current item: if the key already existed, adds one more to the amount.
        """
        item = Item.objects.select_related('shop', 'product').get(pk=item_pk)
        price = str(item.product.price)
        if item_pk not in self.basket:
            self.basket[item_pk] = {
                'amount': 1,
                'shop': item.shop.title,
                'price': price,
            }
        else:
            if item.quantity > self.basket[item_pk]['amount']:
                self.basket[item_pk]['amount'] += 1
        self.save_session()

    def decrease_amount(self, item_pk: str) -> None:
        """
        Decreases the amount of the already stored item in the basket data.
        """
        if item_pk in self.basket:
            self.basket[item_pk]['amount'] -= 1
            if self.basket[item_pk]['amount'] < 1:
                self.delete_product(item_pk)
            else:
                self.save_session()

    def delete_product(self, item_pk: str) -> None:
        """
        Removes the item from the basket
        """
        if item_pk in self.basket:
            del self.basket[item_pk]
        self.save_session()

    def __iter__(self):
        """
        Updates the data of every item stored: the keys are used to retrieve the instances and then they are
        saved as new keys.
        After it, adds the key total_price.
        As a result yields an item from the basket.
        """
        if not self.basket:
            return None
        basket = copy.deepcopy(self.basket)
        item_ids = basket.keys()
        items = Item.objects.select_related('product', 'shop').filter(id__in=item_ids)

        for item in items:
            basket[str(item.id)]['item'] = item
        for cur_item in basket.values():
            cur_item['total_price'] = Decimal(cur_item['price']) * cur_item['amount']
            yield cur_item

    def __len__(self) -> int:
        """
        Calculates the total amount of all items stored in the basket data.
        """
        return sum(item['amount'] for item in self.basket.values())

    def clear_basket(self) -> None:
        """
        Deletes the data from the basket
        """
        del self.session[settings.BASKET_SESSION_ID]
        self.session.modified = True

    def total_sum(self) -> Decimal:
        """
        Calculates the total price of the items stored in the basket.
        """
        return sum(Decimal(item['price']) * item['amount'] for item in self.basket.values())

