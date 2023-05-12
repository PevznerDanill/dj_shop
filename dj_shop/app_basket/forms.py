from django import forms


class BasketAddForm(forms.Form):
    """
    A form for the basket.
    """
    delete_item = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput,
    )

    def __init__(self, amount, *args, **kwargs) -> None:
        """
        When is initiated, looks at the amount and sets the amount field.
        This allows to avoid adding more items to the basket then exist.
        """
        super().__init__(*args, **kwargs)

        max_amount = amount
        self.fields['amount'] = forms.TypedChoiceField(
            choices=[(i, str(i)) for i in range(1, max_amount + 1)],
            coerce=int
        )