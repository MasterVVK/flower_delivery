# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Добавьте любые дополнительные поля, если необходимо
    pass
