from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets, status
from rest_framework.response import Response
from api.permissions import (IsAdminModeratorAuthorOrReadOnly,
                             IsAdminUserOrReadOnly,
                             IsAdmin,
                             IsAdminModeratorAuthorOrReadOnly,
                             )
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, )
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (UserSerializer,
                          GetTokenSerializer,
                          UsersMeSerializer,
                          SignupSerializer,
                          )
from rest_framework.views import APIView
from user.models import User
from api.utils import send_confirmation_code_to_email


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


class UserMeViewSet(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        me = request.user
        serializer = UserSerializer(me)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        me = request.user
        serializer = UsersMeSerializer(me, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        email = request.data.get('email')
        username = request.data.get('username')
        if User.objects.filter(username=username, email=email).exists():
            return Response(
                'Пользователь с таким адресом электронной '
                'почты и именем уже существует',
                status=status.HTTP_200_OK
            )
        if User.objects.filter(
                email=email
        ).exists():
            return Response(
                'Пользователь с таким адресом электронной '
                'почты уже существует',
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_confirmation_code_to_email(request)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenView(TokenObtainPairView):
    # serializer_class = GetTokenSerializer

    permission_classes = [AllowAny, ]

    def post(self, request):
        if not request.data.get('username'):
            return Response(
                'Нет поля username',
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = GetTokenSerializer(data=request.data)
        user = get_object_or_404(User, username=request.data.get('username'))
        if user.confirmation_code != request.data.get('confirmation_code'):
            return Response(
                'Неверный код доступа',
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.is_valid(raise_exception=True)
        token = AccessToken.for_user(user)
        return Response(str(token), status=status.HTTP_200_OK)
