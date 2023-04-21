import random

from django.conf import settings
from django.core.mail import send_mail
from rest_framework.generics import get_object_or_404
from django.utils.crypto import get_random_string
from user.models import User


def send_confirmation_code_to_email(request):
    user = get_object_or_404(User, username=request.data.get('username'))
    confirmation_code = get_random_string(20, settings.CONFIRMATION_CODE_LENGTH)

    user.confirmation_code = confirmation_code
    user.save()
    send_mail(
        'Код подтвержения для завершения регистрации',
        f'Ваш код для получения JWT токена {user.confirmation_code}',
        settings.ADMIN_EMAIL,
        [request.data.get('email')],
        fail_silently=False,
    )
