from api.permissions import IsAdmin
from api.utils import send_confirmation_code_to_email
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated, )
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from user.models import User

from .serializers import (
    UserSerializer,
    GetTokenSerializer,
    UsersMeSerializer,
    SignupSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для модели User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'path',
                         'delete', 'patch')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = [IsAuthenticated, IsAdmin, ]

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            serializer = UsersMeSerializer(request.user,
                                           data=request.data,
                                           partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class SignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            user = get_object_or_404(User, username=username)
            serializer = SignupSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data['email'] != user.email:
                return Response(
                    'Почта указана неверно!', status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save(raise_exception=True)
            send_confirmation_code_to_email(request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if User.objects.filter(
                email=serializer.validated_data['email']
        ).exists():
            return Response(
                'Пользователь с таким адресом электронной '
                'почты уже существует',
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.validated_data['username'] != 'admin':
            serializer.save()
            send_confirmation_code_to_email(request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            (
                f'Использование имени пользователя '
                f'admin запрещено!'
            ),
            status=status.HTTP_400_BAD_REQUEST
        )


class GetTokenView(TokenObtainPairView):
    serializer_class = GetTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            return Response(
                'Неверный код доступа',
                status=status.HTTP_400_BAD_REQUEST
            )
        token = AccessToken.for_user(user)
        return Response(str(token), status=status.HTTP_200_OK)
