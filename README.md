# Учёт заявок ИТ-отдела — лабораторная №0.1

## Запуск на Windows

Из папки `C:\Django_Labs` (или из корня клонированного репозитория):

```powershell
cd .\helpdesk
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver 8003
```

Открыть http://127.0.0.1:8003/. Если вы уже находитесь в папке `helpdesk`, строку `cd .\helpdesk` пропустите. Это сайт заявок ИТ-отдела, а не магазин. Для остановки сервера нажмите `Ctrl+C` в том же окне PowerShell. Тесты: `.\.venv\Scripts\python.exe manage.py test`.

## Учётные записи и возможности

- `ivanov` / `Zayavka-2026` — сотрудник: создаёт заявки, видит только свои, редактирует новые.
- `petrov` / `Zayavka-2026` — ИТ-специалист: видит все заявки, ищет и фильтрует, назначает исполнителя и меняет статус.
- Администратора создать командой `.\.venv\Scripts\python.exe manage.py createsuperuser`; он ведёт категории и пользователей через `/admin/`.

Для демонстрации: войти как `ivanov`, создать заявку и попробовать короткую тему; открыть чужую заявку по номеру; войти как `petrov`, найти заявку и перевести её в работу; снова войти как `ivanov` и проверить, что редактирование запрещено.

Проект учебный. Секретный ключ и режим отладки предназначены только для локального запуска.
