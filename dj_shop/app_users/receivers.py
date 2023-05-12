from django.dispatch import receiver
from .signals import add_balance_signal
import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.utils.translation import gettext_lazy as _
from .models import Profile


user_logger = logging.getLogger("user")


@receiver(add_balance_signal)
def add_balance_receiver(sender: Profile, **kwargs):
    """
    Receives the signal every time a user increases its balance and loggs it.
    """
    user = kwargs.get('user')
    new_amount = kwargs.get('new_amount')
    cur_balance = kwargs.get('cur_balance')
    logg_text = _('The user {user} has just add ${new_amount} to his balance and now it is ${cur_balance}').format(
        user=user,
        new_amount=new_amount,
        cur_balance=cur_balance
    )
    user_logger.info(logg_text)


@receiver(user_logged_in)
def log_user_login(sender, user, **kwargs):
    """
    Logs a new login.
    """
    user_logger.info(_('The user {user} has just logged in').format(user=user))


@receiver(user_login_failed)
def log_user_login_failed(sender, user=None, **kwargs):
    """
    Logs failed attempt of a login.
    """
    if user:
        user_logger.info(_('Failed login of {user}').format(user=user))
    else:
        user_logger.error(_('Failed login of unknown user'))


@receiver(user_logged_out)
def log_user_logout(sender, user, **kwargs):
    """
    Logs logg out.
    """
    user_logger.info(f'The user {user} logged out')
