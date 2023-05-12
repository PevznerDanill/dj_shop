from django.urls import path
from .views import BasketUpdateView


app_name = 'app_basket'

urlpatterns = [
    path('', BasketUpdateView.as_view(), name='basket_detail'),
]
