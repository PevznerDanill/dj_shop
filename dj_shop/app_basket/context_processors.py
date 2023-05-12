from .basket import Basket
from django.http import HttpRequest
from typing import Dict


def basket(request: HttpRequest) -> Dict[str, Basket]:
    """
    Sets the basket object.
    """
    return {'basket': Basket(request)}
