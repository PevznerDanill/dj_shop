from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import logging
from .signals import add_balance_signal
from decimal import Decimal


logger = logging.getLogger(__name__)


class Profile(models.Model):
    """
    Describes the Profile model, the status and discount logic:
    By default, the new Profile has a status 0 (New customer).
    After first five orders gets upgraded to 1 (Advanced customer) and after first ten to Loyal buyer.
    The count of the orders is stored in orders_count field.
    If orders_count is five or more, a discount of 5 per cent is available.
    If orders_count is ten or more, a discount of 10 per cent is available.
    Once used, the orders_count gets decreased by 10, if a 10 per cent discount was used, and by 5, if a
    5 per cent discount was used, and the availability of the discount get updated.
    The status is saved once achieved and isn't changed (can be only upgraded).
    """
    user = models.ForeignKey(to=User, related_name='profile', on_delete=models.CASCADE, verbose_name=_('user'))
    balance = models.DecimalField(default=0, decimal_places=2, verbose_name=_('balance'), max_digits=10*6)
    status = models.IntegerField(default=0, verbose_name=_('status'))
    discount = models.IntegerField(default=0, verbose_name=_('discount'))
    orders_count = models.IntegerField(default=0, verbose_name=_('orders count'))

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def status_str(self) -> str:
        """
        Retruns a string representation of the status of the Profile
        """
        status_dict = {
            0: _('New customer'),
            1: _('Advanced customer'),
            2: _('Loyal buyer'),
        }

        return status_dict[self.status]

    def add_balance(self, new_amount: Decimal) -> None:
        """
        Adds the passed amount to the balance and sends a signal.
        """
        self.balance += new_amount
        self.save(force_update=['balance'])
        add_balance_signal.send(
            sender=self.__class__,
            user=self.user.username,
            new_amount=new_amount,
            cur_balance=self.balance,
        )

    def update_status(self) -> None:
        """
        Updates the current status of the Profile and generates a logg message if
        it is upgraded.
        """
        total_orders = self.orders.count()
        current_status = self.status
        if total_orders >= 5:
            self.status = 1
            self.discount_level = 1
        elif total_orders >= 10:
            self.status = 2
            self.discount_level = 2

        if current_status != self.status:
            logg_text = _('The user {username} has been just updated '
                          'to the status of {status}').format(
                username=self.user.username,
                status=self.status_str()
            )
            logger.info(logg_text)

    def update_discount(self) -> None:
        """
        Updates the available discount. Can be 0, 5 or 10.
        """
        if self.orders_count < 5:
            self.discount = 0
        elif self.orders_count >= 5:
            self.discount = 5
        elif self.orders_count >= 10:
            self.discount = 10

    def use_discount(self, discount_used: str) -> None:
        """
        Uses the discount: subtracts the orders_count and calls self.update_discount() method.
        """
        discount_used = int(discount_used)
        self.orders_count -= discount_used
        self.update_discount()
