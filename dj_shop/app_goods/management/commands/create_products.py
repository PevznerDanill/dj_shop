from django.core.management import BaseCommand
from app_goods.models import Product
from random import randint
from decimal import Decimal


class Command(BaseCommand):
    """
    Creates new products.
    """
    basic_titles = [
        'Computer', 'Smartphone', 'Monitor', 'Vacuum', 'Laptop',
    ]

    titles = [
        f'{basic_title} series {i}'
        for basic_title in basic_titles
        for i in range(1, 6)
    ]

    def handle(self, *args, **options):
        self.stdout.write(f'Creating new {len(self.titles)} products...')
        product_instances = [
            Product(
                title=title,
                price=Decimal(randint(100, 1000))
            )
            for title in self.titles
        ]

        Product.objects.bulk_create(product_instances)
        self.stdout.write(self.style.SUCCESS('All products created'))
