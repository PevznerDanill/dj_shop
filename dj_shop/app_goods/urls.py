from django.urls import path
from django.shortcuts import redirect
from .views import (
    OrderCreateView,
    ShopListView,
    ShopView,
    OrderDetailView,
    OrderListView,
    ReportView
)

app_name = 'app_goods'

urlpatterns = [
    path('', lambda req: redirect('shops/')),
    path('shops/', ShopListView.as_view(), name='shop_list'),
    path('order-create/', OrderCreateView.as_view(), name='order_create'),
    path('shop/<int:pk>/', ShopView.as_view(), name='shop'),
    path('order-detail/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/', OrderListView.as_view(), name='order_list'),
    path('report/', ReportView.as_view(), name='report')
]
