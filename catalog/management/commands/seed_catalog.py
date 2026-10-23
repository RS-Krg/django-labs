from decimal import Decimal

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


class Command(BaseCommand):
    help = 'Заполняет каталог демонстрационными категориями и товарами'

    def handle(self, *args, **options):
        created = 0
        for (name, slug), rows in CATALOG.items():
            category, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            for product_name, product_slug, price, stock in rows:
                _, is_new = Product.objects.get_or_create(slug=product_slug, defaults={
                    'category': category, 'name': product_name, 'price': Decimal(price),
                    'stock': stock, 'description': 'Учебный товар. Описание заполняется в admin panel.',
                })
                created += is_new
        self.stdout.write(self.style.SUCCESS(f'Готово. Новых товаров: {created}'))
