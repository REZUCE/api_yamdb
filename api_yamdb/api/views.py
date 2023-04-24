from django.conf import settings
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status, generics
from rest_framework.response import Response
from api.filters import FilterTitle
from api.mixins import ModelMixinSet
from api.permissions import (IsAdminModeratorAuthorOrReadOnly,
                             IsAdminUserOrReadOnly,
                             IsAdmin,
                             IsAdminModeratorAuthorOrReadOnly,
                             )
from rest_framework.permissions import (AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (UserSerializer, CategorySerializer,
                          CommentsSerializer, GenreSerializer,
                          ReviewSerializer, TitleReadSerializer,
                          TitleWriteSerializer, UsersMeSerializer,
                          SignupSerializer, GetTokenSerializer,
                          )
from reviews.models import Category, Genre, Review, Title
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
        try:
            me = User.objects.get(username=request.user.username)
        except User.DoesNotExists:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(me)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        try:
            me = User.objects.get(username=request.user.username)
        except User.DoesNotExists:
            return Response(status=status.HTTP_404_NOT_FOUND)
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
        # if User.objects.filter(username=self.request.get('username')):
        #     return Response(
        #         'Пользователь с таким адресом электронной почты уже существует',
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        if User.objects.filter(username=username, email=email).exists():
            return Response(
                'Пользователь с таким адресом электронной почты и именем уже существует',
                status=status.HTTP_200_OK
            )
        if User.objects.filter(
                email=email
        ).exists():
            return Response(
                'Пользователь с таким адресом электронной почты уже существует',
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
            return Response('Нет поля username', status=status.HTTP_400_BAD_REQUEST)
        serializer = GetTokenSerializer(data=request.data)
        user = get_object_or_404(User, username=request.data.get('username'))
        if user.confirmation_code != request.data.get('confirmation_code'):
            return Response('Неверный код доступа', status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        token = AccessToken.for_user(user)
        return Response(str(token), status=status.HTTP_200_OK)


class CategoryViewSet(ModelMixinSet):
    """Category для модели User"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
    """Genre для модели User"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Title"""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score'),
    ).all()
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterTitle

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Review"""
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAdminModeratorAuthorOrReadOnly,
    )

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user, title=title)
        return Response(status=status.HTTP_201_CREATED)


class testviewsset(viewsets.ModelViewSet):
    pass


class CommentsViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Comments"""
    serializer_class = CommentsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAdminModeratorAuthorOrReadOnly,)

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'),
        )
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'),
        )
        return review.comments.all()
