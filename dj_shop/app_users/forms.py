from django import forms
from django.utils.translation import gettext_lazy as _


class AddBalance(forms.Form):
    """
    A form to top up the balance.
    """
    balance = forms.DecimalField(min_value=0, max_digits=10**6, decimal_places=2,
                                 label=_('Enter the amount you want to add to your balance'),
                                 max_value=10**6)
