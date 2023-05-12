import logging
from .models import Order
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger('order')


@receiver(post_save, sender=Order)
def new_order_receiver(sender, instance: Order, created, **kwargs):
    """
    If the signal is received, generates a message and passes it to the order.log.
    """
    if created:
        user = instance.profile.user.username
        log_text = _('The user {user} has just made a new order').format(user=user)
        logger.info(log_text)
