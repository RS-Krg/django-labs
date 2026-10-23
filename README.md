# Учебный магазин компьютерной техники — лабораторные №0.2 и №0.3

## Запуск на Windows

```powershell
cd shop
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_catalog
.\.venv\Scripts\python.exe manage.py runserver
```

Каталог: http://127.0.0.1:8000/. Администратора создают через `manage.py createsuperuser`.
Тесты: `.\.venv\Scripts\python.exe manage.py test`.

Каталог содержит категории, активные товары, фото, поиск по кириллице без учёта регистра, сортировку и постраничный вывод. Для демонстрации запустите `seed_catalog` дважды: второй запуск сообщит о нуле новых товаров. Затем найдите «МОНИТОР», выберите сортировку и перейдите на страницу товара.
