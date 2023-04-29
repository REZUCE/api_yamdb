from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

USERNAME_CHECK = r'^[\w.@+-]+$'  # Проверка имени на отсутствие спецсимволов


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=USERNAME_CHECK,
                message="""Имя должно содержать,только
                буквы,
                цифры или же символ подчеркивания!"""),
            UniqueValidator(queryset=User.objects.all()),
        ],
    )

    class Meta:
        fields = ('username', 'email',
                  'first_name', 'last_name',
                  'bio', 'role')
        model = User


class UsersMeSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=20)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        if not username:
            raise serializers.ValidationError('Нет поля username')

        try:
            user = get_object_or_404(User, username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('Пользователь с таким именем не найден')

        if user.username != username:
            return Response(
                {'detail': 'Неверный код доступа'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError('Неверный код доступа')

        return data


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""
    email = serializers.EmailField(max_length=254)

    class Meta:
        fields = ('username', 'email')
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'me нельзя использовать в качестве имени',
            )
        return value
