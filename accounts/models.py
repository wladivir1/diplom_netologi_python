from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from .managers import UserManager

# Create your models here.
USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),

)


class User(AbstractUser):
    """
    Модель пользователя для входа в систему и регистрации.
    """
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = UserManager()
    USERNAME_FIELD = 'email'
    surname = models.CharField(verbose_name='Фамилия', max_length=30, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    phone = models.CharField(verbose_name='Телефон', max_length=20, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        app_label = 'accounts'
        ordering = ('email',)
        
        
    def __str__(self) -> str:
        """ Магический метод для представления объекта в консоли. """
        return self.email        
        
        
class Contact(models.Model):
    """ Модель для работы с контактами пользователя """
    objects = models.manager.Manager()
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='contacts', blank=True,
                             on_delete=models.CASCADE)
    index = models.CharField(max_length=6, verbose_name='Индекс', blank=True)
    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self) -> str:
        """ Магический метод для представления объекта в консоли. """
        return f'{self.city} {self.street} {self.house}'        