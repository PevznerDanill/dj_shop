from django import forms
from django.utils.translation import gettext_lazy as _
from app_users.models import Profile


class OrderForm(forms.Form):
    """
    A form to crate an order. Only uses delivery address and if used or not the discount
    information, because the main information is being gotten from the basket.
    """

    delivery_address = forms.CharField(max_length=200, label='Delivery address')
    DISCOUNT_CHOICES = [
        ('', _('No discount')),
        ('5', _('5% discount')),
        ('10', _('10% discount')),
    ]

    def __init__(self, profile: Profile = None, *args, **kwargs) -> None:

        """
        When is initiated looks if the current profile has a discount available and
        according to this data creates a discount field.
        """
        super().__init__(*args, **kwargs)
        if profile:
            profile_discount = profile.discount
            if profile_discount == 5:
                self.fields['discount'] = forms.ChoiceField(choices=self.DISCOUNT_CHOICES[:2], required=False)
            elif profile_discount == 10:
                self.fields['discount'] = forms.ChoiceField(choices=self.DISCOUNT_CHOICES, required=False)
