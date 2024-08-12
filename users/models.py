from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Администратор'),
        ('Manager', 'Менеджер'),
        ('User', 'Пользователь'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Измените related_name здесь
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Измените related_name здесь
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username
