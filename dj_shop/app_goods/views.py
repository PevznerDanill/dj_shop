from django.core.exceptions import PermissionDenied
from django.shortcuts import reverse, get_object_or_404, redirect
from django.db.models import DecimalField
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView, DetailView, View
from .models import Shop, Product, Order, Item
from app_basket.forms import BasketAddForm
from app_users.models import Profile
from .forms import OrderForm
from app_basket.basket import Basket
from django.db import connection
from django.db.models import Prefetch, Count, Subquery, OuterRef, Q, F, Exists, Sum, ExpressionWrapper
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.conf import settings
import copy
from django.db import transaction
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from typing import Dict, Union, Optional
from decimal import Decimal


class ShopListView(ListView):
    """
    A view to display a list of shops.
    """
    queryset = (
        Shop.objects.all
    )
    template_name = 'app_goods/shop_list.html'
    context_object_name = 'shops'

    def get_context_data(self, *, object_list=None, **kwargs) -> Dict[str, Union[View, Basket, Profile]]:
        """
        Adds the Profile instance and basket data to the context if request.user.is_authenticated.
        """
        context = super().get_context_data(object_list=None, **kwargs)
        if self.request.user.is_authenticated:
            context['profile'] = get_object_or_404(Profile, user=self.request.user)
            basket = Basket(self.request)
            context['basket'] = basket
        return context


class OrderCreateView(LoginRequiredMixin, TemplateView):
    """
    A view for the order creation form.
    """

    template_name = 'app_goods/order_create.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Adds form to the context.
        """
        profile = get_object_or_404(Profile, user=self.request.user)
        form = OrderForm(profile=profile)
        context = {
            'form': form,
        }
        return self.render_to_response(context)


class OrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    A view to display the details of the retrieved order.
    """
    queryset = (
        Order.objects.select_related('profile').
        prefetch_related(Prefetch(
            'items', queryset=Item.objects.select_related('product')
        )).annotate(total_items=Count('items')).annotate(
            total_price=Sum(ExpressionWrapper(
                F('items__product__price') * F('items__ordered_quantity'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ))
        )
    )
    template_name = 'app_goods/order_detail.html'
    context_object_name = 'order'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Overrides the default get method removing from it the declaration
        of the self.object attribute, as it was defined in self.setup().
        """
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """
        Declares the self.object and self.profile (Profile related to the User from
        request.user) attributes.
        """
        super().setup(request, *args, **kwargs)
        self.object = self.get_object()
        self.profile = get_object_or_404(Profile, user=self.request.user)

    def test_func(self) -> bool:
        """
        Checks if the current profile instance is the same as the profile field in order, or
        if the current user is superuser.
        """
        return self.profile == self.object.profile or self.request.user.is_superuser

    def get_context_data(self, **kwargs) -> Dict[str, Union[Decimal, Order, View, Profile]]:
        """
        Gets from the order queryset the annotated field total_price and applies to it
        discount if it exists.
        Adds it to the context, as well as profile instance.
        """
        context = super().get_context_data(**kwargs)
        order = context['order']
        total_price = order.total_price
        if order.discount:
            total_price -= total_price / 100 * int(order.discount)
        context['total_price'] = total_price
        context['profile'] = self.profile
        return context


class ShopView(TemplateView):
    """
    A view to display the items of the retrieved shop.
    """
    template_name = 'app_goods/shop.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Adds the data of the shop and its items to the context.
        If the user is authenticated, also adds the profile instance and the basket data.
        """
        context = self.get_context_data(**kwargs)
        pk = kwargs['pk']
        shop = Shop.objects.get(pk=pk)
        items = Item.objects.select_related('shop', 'product').filter(
            Q(quantity__gt=1) & Q(shop=shop)
        )
        context['items'] = items
        context['shop'] = shop
        if self.request.user.is_authenticated:
            context['profile'] = get_object_or_404(Profile, user=self.request.user)
            context['basket'] = Basket(request)
        return self.render_to_response(context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        For the authenticated users, adds an item to the basket.
        """
        if not request.user.is_authenticated:
            return redirect(reverse('app_users:login'))

        basket = Basket(request)
        item_pk = request.POST.get('basket_item')
        basket.add_product(item_pk)
        cur_item = Item.objects.select_related('product', 'shop').get(pk=item_pk)
        success_msg = _('{item} successfully added to the basket').format(
            item=cur_item.product.title,
        )
        messages.success(request, success_msg)
        return HttpResponseRedirect(reverse('app_goods:shop', kwargs={'pk': cur_item.shop.pk}))


class OrderListView(LoginRequiredMixin, TemplateView):
    """
    Shows the orders of the current user.
    It needs only LoginRequiredMixin and not UserPassesTest, as the data retrieved
    is related to the User instance saved in request.user.
    """
    template_name = 'app_goods/order_list.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Adds the basket data and the profile instance to the context.
        """
        context = self.get_context_data(**kwargs)
        profile = get_object_or_404(Profile, user=request.user)
        basket = Basket(self.request)
        context.update(
            {
                'profile': profile,
                'basket': basket,
                'orders': Order.objects.prefetch_related(
                    Prefetch(
                        'items', queryset=Item.objects.select_related('product')
                    )
                ).select_related('profile').annotate(
                    total_items=F('items__ordered_quantity') * Count('items')
                ).
                annotate().filter(profile__id=profile.pk)
            }
        )

        return self.render_to_response(context)


class ReportView(UserPassesTestMixin, TemplateView):
    """
    A view to display the Report. Available only for superuser or staff.
    """
    template_name = 'app_goods/report.html'

    def test_func(self) -> bool:
        """
        Checks if the user is staff or is superuser.
        """
        return self.request.user.is_staff or self.request.user.is_superuser

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Adds the data to display the top sold products in a selected period.
        """
        context = self.get_context_data(**kwargs)
        orders = Order.objects.prefetch_related('items').all()

        start_date = self.request.POST.get('start_date')

        end_date = self.request.POST.get('end_date')

        if start_date and end_date:

            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d')) + timedelta(days=1)
            orders = orders.filter(
                created_at__range=[start_date, end_date]
            )
        top_items = Item.objects.select_related('product', 'shop').filter(
            Q(orders__in=orders)
        ).order_by('-ordered_quantity')
        total_sold = sum(item.ordered_quantity for item in top_items)

        context['top_items'] = top_items
        context['total_sold'] = total_sold
        return self.render_to_response(context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Returns the get method with the selected period of time.
        """
        return self.get(request, *args, **kwargs)
