from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse, redirect
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from .basket import Basket
from app_goods.forms import OrderForm
from app_users.models import Profile
from django.views.generic import TemplateView
from .utils import process_request
from django.db import transaction
from .utils import spend_money, take_products_from_shops, create_order
from django.utils.translation import gettext_lazy as _


class BasketUpdateView(LoginRequiredMixin, TemplateView):
    """
    A view for the basket update
    """
    template_name = 'app_basket/basket_detail.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Takes the basket data from the session, the profile instance related
        to the User instance saved in request.user and adds it to the context for rendering.
        Also calculates if the profile's balance is enough to make an order. If not, displays
        a warning message.
        """
        context = self.get_context_data(**kwargs)
        basket = Basket(request)
        cur_profile = Profile.objects.get(user=request.user)
        warning_message = None
        if basket.total_sum() > cur_profile.balance:
            warning_message = _('You need to top up your balance to be able to create this order')
        context['basket'] = basket
        context['profile'] = cur_profile
        context['warning_message'] = warning_message
        return self.render_to_response(context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        Processes the data from the request.POST to edit the basket or to create a new order.
        """
        profile = Profile.objects.get(user=self.request.user)
        if request.POST.__contains__('delivery_address'):
            address_form = OrderForm(data=self.request.POST, profile=profile)
            if address_form.is_valid():
                address = address_form.cleaned_data['delivery_address']
                discount = address_form.cleaned_data.get('discount')
                if discount is None:
                    discount = ''
                basket = Basket(self.request)

                with transaction.atomic():
                    total_sum = spend_money(profile=profile, basket=basket, discount=discount)
                    items = take_products_from_shops(basket=basket)
                    new_order_pk = create_order(products_taken=items, address=address,
                                                profile=profile, discount=discount)
                return redirect(reverse('app_goods:order_detail', kwargs={'pk': new_order_pk}))

        anchor = process_request(request)
        reversed_url = reverse('app_basket:basket_detail') + anchor
        return redirect(reversed_url)
