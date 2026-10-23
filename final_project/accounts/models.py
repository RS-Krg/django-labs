from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Пользователь магазина; создан до первой миграции."""
