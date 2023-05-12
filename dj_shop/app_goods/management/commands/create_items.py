from django.core.management import BaseCommand
from app_goods.models import Shop, Product, Item


class Command(BaseCommand):
    """
    Creates new items.
    """
    def handle(self, *args, **options):
        self.stdout.write('Creating new items')
        shops = Shop.objects.all()
        products = Product.objects.all()
        items = []
        for shop in shops:
            for product in products:
                shop_category_0 = shop.title.split(' and ')[0][:-1]
                shop_category_1 = shop.title.split(' and ')[1][:-1]
                if product.title.startswith(shop_category_0):
                    items.append(
                        Item(
                            shop=shop,
                            product=product,
                            supplier=f"{product.title}'s supplier",
                            quantity=10,
                        )
                    )
                if product.title.startswith(shop_category_1):
                    items.append(
                        Item(
                            shop=shop,
                            product=product,
                            supplier=f"{product.title}'s supplier",
                            quantity=10,
                        )
                    )

        Item.objects.bulk_create(items)
        self.stdout.write(self.style.SUCCESS(f'Created {len(items)} new items'))
