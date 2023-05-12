from django.contrib import admin
from .models import Item, Product, Shop, Order

"""
Registers the models Item, Product, Shop and Order in the admin panel.
"""


class OrderInline(admin.TabularInline):
    model = Item.orders.through


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = 'id', 'quantity'
    inlines = [OrderInline]


class ItemInline(admin.StackedInline):
    model = Item


class ItemInlineForOrder(admin.TabularInline):
    model = Order.items.through


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = 'id', 'title', 'price',
    inlines = [ItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = 'id', 'profile', 'created_at'
    inlines = [ItemInlineForOrder]


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = 'id', 'title'
