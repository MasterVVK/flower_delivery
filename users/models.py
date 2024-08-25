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

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)  # Почтовый индекс
    country = models.CharField(max_length=100, default="Россия")
    house = models.CharField(max_length=20)  # Номер дома
    flat = models.CharField(max_length=10, blank=True, null=True)  # Номер квартиры
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.postal_code}, {self.country}"

    @property
    def formatted_address(self):
        address_parts = [
            self.state,
            self.city,
            self.street,
            f"д {self.house}",
            f"кв {self.flat}" if self.flat else None
        ]
        return ', '.join(filter(None, address_parts))

