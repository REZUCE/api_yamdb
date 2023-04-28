from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User

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
