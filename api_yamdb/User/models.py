from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class User(AbstractUser):
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
