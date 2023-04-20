from django.conf import settings
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.response import Response
from api.filters import FilterTitle
from api.mixins import ModelMixinSet
from api.permissions import (IsAdminModeratorAuthorOrReadOnly,
                             IsAdminUserOrReadOnly,
                             IsAdmin,
                             IsAdminModeratorAuthorOrReadOnly,
                             )
from rest_framework.permissions import (AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly)
from .serializers import (UserSerializer, CategorySerializer,
                          CommentsSerializer, GenreSerializer,
                          ReviewSerializer, TitleReadSerializer,
                          TitleWriteSerializer, UsersMeSerializer,
                          SignupSerializer,
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
                         'delete', 'put', 'patch')
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
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if User.objects.filter(username=request.data.get('username'), email=request.data.get('email')):
            send_confirmation_code_to_email(request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_confirmation_code_to_email(request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
    permission_classes = (IsAuthenticated,
                          IsAdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


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
