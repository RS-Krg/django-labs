from decimal import Decimal
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from catalog.models import Category, Product


CATALOG = {
    ('Ноутбуки', 'laptops'): [
        ('Ноутбук 14 Core i3 8 ГБ', 'laptop-14-i3', '38990', 12),
        ('Ноутбук 15 Core i5 16 ГБ', 'laptop-15-i5', '61990', 7),
        ('Ноутбук 16 Core i7 32 ГБ', 'laptop-16-i7', '104990', 3),
        ('Ноутбук 13 для учёбы', 'laptop-13-edu', '27490', 0),
    ],
    ('Мониторы', 'monitors'): [
        ('Монитор 24 IPS Full HD', 'monitor-24-fhd', '12990', 15),
        ('Монитор 27 IPS 2K', 'monitor-27-2k', '21990', 9),
        ('Монитор 32 VA 4K', 'monitor-32-4k', '34990', 4),
        ('Монитор 22 офисный', 'monitor-22-office', '8990', 20),
    ],
    ('Клавиатуры и мыши', 'input'): [
        ('Клавиатура проводная', 'keyboard-office', '990', 50),
        ('Клавиатура механическая', 'keyboard-mechanical', '5490', 11),
        ('Мышь беспроводная', 'mouse-wireless', '1290', 40),
        ('Комплект клавиатура и мышь', 'keyboard-mouse-set', '2190', 25),
    ],
    ('Накопители', 'storage'): [
        ('SSD 512 ГБ M.2 NVMe', 'ssd-512-nvme', '4290', 30),
        ('SSD 1 ТБ M.2 NVMe', 'ssd-1tb-nvme', '7490', 18),
        ('Внешний диск 2 ТБ', 'hdd-external-2tb', '6990', 6),
        ('Флешка 64 ГБ USB 3.2', 'usb-flash-64', '690', 100),
    ],
    ('Сетевое оборудование', 'network'): [
        ('Wi-Fi роутер', 'router-dual-band', '3990', 14),
        ('Коммутатор 8 портов', 'switch-8-port', '2490', 10),
        ('Сетевой кабель 5 м', 'patch-cord-5m', '290', 200),
        ('Wi-Fi адаптер USB', 'wifi-usb-adapter', '990', 0),
    ],
}

DEMO_IMAGES = {
    'ssd-1tb-nvme': 'ssd-1tb-nvme.png',
    'ssd-512-nvme': 'ssd-1tb-nvme.png',
    'wifi-usb-adapter': 'wifi-usb-adapter.png',
    'router-dual-band': 'router-dual-band.png',
    'hdd-external-2tb': 'hdd-external-2tb.png',
    'laptop-14-i3': 'laptop-14-i3.png',
    'laptop-15-i5': 'laptop-15-i5.png',
    'laptop-16-i7': 'laptop-15-i5.png',
    'laptop-13-edu': 'laptop-14-i3.png',
    'monitor-24-fhd': 'monitor-24-fhd.png',
    'monitor-27-2k': 'monitor-27-2k.png',
    'monitor-32-4k': 'monitor-32-4k.png',
    'monitor-22-office': 'monitor-24-fhd.png',
    'keyboard-office': 'keyboard-mechanical.png',
    'keyboard-mechanical': 'keyboard-mechanical.png',
    'keyboard-mouse-set': 'keyboard-mouse-set.png',
    'mouse-wireless': 'mouse-wireless.png',
    'switch-8-port': 'switch-8-port.png',
    'patch-cord-5m': 'patch-cord-5m.png',
    'usb-flash-64': 'usb-flash-64.png',
}


class Command(BaseCommand):
    help = 'Заполняет каталог демонстрационными категориями и товарами'

    def handle(self, *args, **options):
        created = 0
        for (name, slug), rows in CATALOG.items():
            category, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            for product_name, product_slug, price, stock in rows:
                product, is_new = Product.objects.get_or_create(slug=product_slug, defaults={
                    'category': category, 'name': product_name, 'price': Decimal(price),
                    'stock': stock, 'description': 'Учебный товар. Описание заполняется в admin panel.',
                })
                created += is_new
                if not product.image and product_slug in DEMO_IMAGES:
                    image_path = Path(__file__).resolve().parents[2] / 'demo_images' / DEMO_IMAGES[product_slug]
                    with image_path.open('rb') as image_file:
                        product.image.save(DEMO_IMAGES[product_slug], File(image_file), save=True)
        self.stdout.write(self.style.SUCCESS(f'Готово. Новых товаров: {created}'))
