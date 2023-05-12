from django.core.management import BaseCommand
from app_goods.models import categories, Shop


class Command(BaseCommand):
    """
    Creates new shops.
    """
    base_address = 'Moscow, street'

    def prepare_shops(self):
        titles = []
        for i in range(5):
            cur_categories = list(categories)
            cur_category = cur_categories.pop(i)
            for category in cur_categories:
                titles.append(f'{cur_category}s and {category}s')

        addresses = (self.base_address + f' {x}, building {y}'
                     for x in range(1, 3) for y in range(1, 11))

        return zip(titles, addresses)

    def handle(self, *args, **options):
        self.stdout.write('Creating shops...')
        shop_data = self.prepare_shops()
        shops = [
            Shop(
                title=title,
                address=address
            )
            for title, address in shop_data
        ]
        Shop.objects.bulk_create(shops)

        self.stdout.write(self.style.SUCCESS(f'Created {len(shops)} new shops'))

