from decimal import Decimal
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from catalog.models import Brand, Category, Product, ProductVariant


SPORTS = {
    ('Бег', 'running'): [
        ('Кроссовки Tempo', 'tempo-shoes', 'Runway', 'runway', 7990, [('39', 5), ('40', 8), ('41', 6)]),
        ('Кроссовки Sprint', 'sprint-shoes', 'Runway', 'runway', 5990, [('39', 0), ('40', 3)]),
        ('Футболка DryFit', 'dryfit-shirt', 'Runway', 'runway', 1990, [('S', 6), ('M', 10), ('L', 5)]),
        ('Шорты беговые Flow', 'flow-shorts', 'Runway', 'runway', 2490, [('S', 4), ('M', 7)]),
        ('Куртка ветровка Wind', 'wind-jacket', 'Peak', 'peak', 6990, [('M', 3), ('L', 2)]),
    ],
    ('Фитнес', 'fitness'): [
        ('Легинсы Flex', 'flex-leggings', 'Peak', 'peak', 3490, [('S', 5), ('M', 5), ('L', 0)]),
        ('Топ Motion', 'motion-top', 'Peak', 'peak', 2790, [('S', 4), ('M', 6)]),
        ('Перчатки для зала Grip', 'grip-gloves', 'PowerLab', 'powerlab', 1490, [('S', 8), ('M', 10)]),
        ('Пояс силовой Core', 'core-belt', 'PowerLab', 'powerlab', 3990, [('M', 4), ('L', 3)]),
        ('Майка Training', 'training-tank', 'PowerLab', 'powerlab', 1790, [('M', 7), ('L', 4)]),
    ],
    ('Футбол', 'football'): [
        ('Бутсы Striker', 'striker-boots', 'BallPro', 'ballpro', 8990, [('40', 4), ('41', 5), ('42', 3)]),
        ('Бутсы Field', 'field-boots', 'BallPro', 'ballpro', 6490, [('39', 3), ('40', 6)]),
        ('Форма Club', 'club-kit', 'BallPro', 'ballpro', 4990, [('S', 5), ('M', 9), ('L', 6)]),
        ('Гетры Match', 'match-socks', 'BallPro', 'ballpro', 890, [('M', 10), ('L', 12)]),
        ('Вратарские перчатки Save', 'save-gloves', 'BallPro', 'ballpro', 3490, [('8', 3), ('9', 4)]),
    ],
    ('Туризм', 'hiking'): [
        ('Ботинки Trail', 'trail-boots', 'Peak', 'peak', 10990, [('40', 3), ('41', 2), ('42', 4)]),
        ('Куртка Alpine', 'alpine-jacket', 'Peak', 'peak', 12990, [('M', 3), ('L', 2)]),
        ('Рюкзак Trek 30', 'trek-backpack', 'Peak', 'peak', 5990, [('30L', 6)]),
        ('Термобельё Base', 'base-thermal', 'Peak', 'peak', 4490, [('S', 0), ('M', 0), ('L', 0)]),
        ('Носки Trek', 'trek-socks', 'Peak', 'peak', 790, [('M', 15), ('L', 10)]),
    ],
}

DEMO_IMAGES = {
    'tempo-shoes': 'tempo-shoes.png',
    'wind-jacket': 'wind-jacket.png',
    'trail-boots': 'trail-boots.png',
    'striker-boots': 'striker-boots.png',
}


class Command(BaseCommand):
    help = 'Создаёт 20 спортивных товаров с брендами и размерами'

    def handle(self, *args, **options):
        created = 0
        for (category_name, category_slug), products in SPORTS.items():
            category, _ = Category.objects.get_or_create(
                slug=category_slug, defaults={'name': category_name},
            )
            for name, slug, brand_name, brand_slug, price, sizes in products:
                brand, _ = Brand.objects.get_or_create(slug=brand_slug, defaults={'name': brand_name})
                product, is_new = Product.objects.get_or_create(slug=slug, defaults={
                    'name': name, 'category': category, 'brand': brand,
                    'price': Decimal(price), 'description': 'Спортивный товар для тренировок и активного отдыха.',
                })
                created += is_new
                if not product.image and slug in DEMO_IMAGES:
                    image_path = Path(__file__).resolve().parents[2] / 'demo_images' / DEMO_IMAGES[slug]
                    with image_path.open('rb') as image_file:
                        product.image.save(DEMO_IMAGES[slug], File(image_file), save=True)
                for size, stock in sizes:
                    ProductVariant.objects.get_or_create(product=product, size=size, defaults={'stock': stock})
        self.stdout.write(self.style.SUCCESS(f'Готово. Новых спортивных товаров: {created}'))
