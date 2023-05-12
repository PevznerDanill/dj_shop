from django.db import models
from django.utils.translation import gettext_lazy as _
from app_users.models import Profile

categories = (
    'Computer', 'Smartphone', 'Monitor', 'Vacuum', 'Laptop',
)

CHOICES = (
    (str(ind), category) for ind, category in enumerate(categories)
)


class Product(models.Model):
    """
    A model to describe a Product. Represents some kind of a category of items with the basic information
    about it.
    """
    price = models.DecimalField(decimal_places=2, max_digits=5, default=0, verbose_name=_('price'))
    title = models.CharField(max_length=100, verbose_name=_('title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('description'))
    image = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name=_('image'))

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self):
        return self.title


class Shop(models.Model):
    """
    A model to describe a Shop.
    """
    title = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('shop')
        verbose_name_plural = _('shops')


class Item(models.Model):
    """
    Describes Item model.
    """
    product = models.ForeignKey(to=Product, related_name='items',
                                on_delete=models.CASCADE, default=1, verbose_name=_('product'))
    shop = models.ForeignKey(to=Shop, related_name='items', on_delete=models.PROTECT, null=True, verbose_name=_('shop'))
    quantity = models.IntegerField(default=0, verbose_name=_('quantity'))
    supplier = models.CharField(max_length=200, verbose_name=_('supplier'))
    date_added = models.DateField(auto_now=True, verbose_name=_('date added'))
    available = models.BooleanField(default=True, verbose_name=_('available'))
    ordered_quantity = models.IntegerField(default=0, verbose_name=_('ordered_quantity'))

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')

    def __str__(self):
        return self.product.title

    def update_available(self) -> None:
        """
        Changes the flag available to False if the quantity is less then 1.
        """
        if self.quantity < 1:
            self.available = False


class Order(models.Model):
    """
    Describes Order model.
    """
    profile = models.ForeignKey(to=Profile, on_delete=models.CASCADE, related_name='orders', verbose_name=_('profile'))
    items = models.ManyToManyField(to=Item, related_name='orders', verbose_name=_('items'))
    delivery_address = models.CharField(max_length=200, verbose_name=_('delivery address'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    discount = models.IntegerField(default=0, verbose_name=_('discount'))

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
