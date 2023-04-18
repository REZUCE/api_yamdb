from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('user', 'user'),
        ('admin', 'admin'),
        ('moderator', 'moderator')
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    email = models.EmailField(
        verbose_name='Почта',
        max_length=254,
        unique=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=9,
        choices=USER_TYPE_CHOICES,
        default=USER_TYPE_CHOICES[0][0]
    )
    confirmation_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Код доступа',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
