from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .bot_utils import notify_order_cancellation
from django.db.models import Avg

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return f"Корзина {self.user.username if self.user else self.session_key}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class ProductCategory(models.Model):
    name = models.CharField(_("Название категории"), max_length=100)
    description = models.TextField(_("Описание"), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Категория продукта")
        verbose_name_plural = _("Категории продуктов")

class Product(models.Model):
    name = models.CharField(_("Название"), max_length=100)
    price = models.DecimalField(_("Цена"), max_digits=10, decimal_places=2)
    image = models.ImageField(_("Изображение"), upload_to='products/')
    category = models.ForeignKey(ProductCategory, verbose_name=_("Категория"), on_delete=models.CASCADE, related_name='products')
    description = models.TextField(_("Описание"), blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def avg_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    class Meta:
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукты")

class Order(models.Model):
    STATUS_CHOICES = [
        ('P', 'В ожидании'),
        ('C', 'Завершен'),
        ('F', 'Неудачно'),
        ('X', 'Отменен'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Пользователь"), on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', verbose_name=_("Продукты"), through='OrderProduct')
    status = models.CharField(_("Статус"), max_length=1, choices=STATUS_CHOICES, default='P')
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    delivery_address = models.ForeignKey('users.Address', verbose_name=_("Адрес доставки"), on_delete=models.SET_NULL, null=True, blank=True)


    def cancel(self):
        if self.status == 'P':
            self.status = 'X'
            self.save()
            notify_order_cancellation(self)

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, verbose_name=_("Заказ"), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_("Продукт"), on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_("Количество"))

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    class Meta:
        verbose_name = _("Продукт заказа")
        verbose_name_plural = _("Продукты заказа")

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Пользователь"), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_("Продукт"), on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(_("Рейтинг"))
    comment = models.TextField(_("Комментарий"))
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)

    def __str__(self):
        return f"Отзыв {self.id} от {self.user.username}"

    class Meta:
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")


class Report(models.Model):
    date = models.DateField(_("Дата"))
    total_sales = models.DecimalField(_("Общие продажи"), max_digits=10, decimal_places=2)
    total_orders = models.PositiveIntegerField(_("Общее количество заказов"))

    def __str__(self):
        return f"Отчет за {self.date}"

    class Meta:
        verbose_name = _("Отчет")
        verbose_name_plural = _("Отчеты")
