from django.db import models
from django.dispatch import receiver
from django.conf import settings
from versatileimagefield.fields import VersatileImageField, PPOIField

from accounts.models import Contact


STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

STATUS_CHOICES = (
    ('open', 'Открыто'),
    ('closed', 'Закрыто'),
)


# Create your models here.
class Shop(models.Model):
    objects = models.manager.Manager()

    name = models.CharField(max_length=50, verbose_name='Название магазина')
    url = models.URLField(verbose_name='Ссылка на магазин',
                          blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    status = models.CharField(verbose_name='Статус приема заявок',
                              choices=STATUS_CHOICES, max_length=15,
                              default="closed")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ['-name']

    def __str__(self):
        return f'{self.name} {self.url} {self.user}'


class Category(models.Model):
    objects = models.manager.Manager()

    name = models.CharField(max_length=50, verbose_name='Название категории')
    shop = models.ManyToManyField(Shop, related_name='categories', verbose_name='Магазин')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['-name']

    def __str__(self):
        return f'{self.name}'


class Product(models.Model):
    objects = models.manager.Manager()

    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 verbose_name='Категория',
                                 related_name='products')
    name = models.CharField(max_length=50, verbose_name='Название продукта')
    image = VersatileImageField('Изображение',
                                upload_to='product_images/', blank=True, null=True,
                                ppoi_field='image_ppoi')
    
    image_ppoi = PPOIField()

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-name']

    def __str__(self):
        return f'{self.name} {self.category}'


class ProductInfo(models.Model):
    objects = models.manager.Manager()
    model = models.CharField(max_length=150, verbose_name="Модель",blank=True)
    external_id = models.PositiveIntegerField(verbose_name="Внешний ID")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE,
                             verbose_name="Магазин",
                             related_name="product_infos", blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name="Продукт",
                                related_name="product_infos", blank=True)
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.PositiveIntegerField(verbose_name="Цена")
    price_rrc = models.PositiveIntegerField(verbose_name="Розничная цена")

    class Meta:
        verbose_name = "Информация о продукте"
        verbose_name_plural = "Информация о продуктах"
        ordering = ('-product',)
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], 
                                    name='unique_product_info'),
        ]

    def __str__(self):
        return f'{self.model} {self.shop.name} {self.product.name} {self.quantity} {self.price}'


class Parameter(models.Model):
    objects = models.manager.Manager()
    
    name = models.CharField(max_length=50, verbose_name='Название параметра')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    objects = models.manager.Manager()

    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE,
                                     verbose_name='Информация о продукте',
                                     related_name='product_parameters')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE,
                                  verbose_name='Параметр',
                                  related_name='product_parameters')
    value = models.CharField(max_length=200, verbose_name='Значение')

    class Meta:
        verbose_name = 'Описание параметра'
        verbose_name_plural = 'Описание параметров'
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'],
                                    name='unique_product_parameter'),
        ]
        ordering = ('-parameter',)

    def __str__(self):
        return f'{self.product_info} {self.parameter} {self.value}'

    
class Order(models.Model):
    objects = models.manager.Manager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    state = models.CharField(verbose_name='Статус', choices=STATE_CHOICES,
                             default="basket", max_length=15)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user} {self.created_at} {self.state}'


class OrderItem(models.Model):
    objects = models.manager.Manager()

    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              verbose_name='Заказ',
                              related_name='ordered_items')
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE,
                                     verbose_name='Информация о продукте',
                                     related_name='ordered_items')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE,
                                verbose_name='Контакты',
                                related_name='ordered_items',
                                null=True, blank=True)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Описание заказа'
        verbose_name_plural = 'Описание заказов'
        ordering = ('-order',)

    def __str__(self):
        return f'{self.order} {self.product_info} {self.quantity} {self.contact}'
