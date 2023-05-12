from django.core.management import BaseCommand
import os
from django.core.files import File
from app_goods.models import Product


class Command(BaseCommand):
    """
    Adds images to the products.
    Current get_images class method uses local path to the images, that can be changed.
    """

    @classmethod
    def get_images(cls, path_to_imgs=None):
        if path_to_imgs:
            return os.path.abspath(path_to_imgs)
        some_dir = os.path.abspath(os.path.join(
            os.sep, 'Users', 'daniilpevzner', 'Desktop', 'your_shops_imgs')
        )
        return some_dir

    def handle(self, *args, **options):
        self.stdout.write('Starting to add images')
        images_dir = self.get_images()
        categories = Product.objects.all()
        for category in categories:
            category_title = category.title
            category_img_title = f'{category_title}.webp'
            img_path = os.path.join(images_dir, category_img_title)
            if os.path.exists(img_path):
                with open(img_path, 'rb') as image_file:
                    django_file = File(image_file)
                    category.image.save(category_img_title, django_file, save=True)
                    self.stdout.write(f'Added an imgage to {category_title}')

        self.stdout.write(self.style.SUCCESS('Added all images'))

