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
                             IsAdminOrStaff
                             )
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from .serializers import (UserSerializer, CategorySerializer,
                          CommentsSerializer, GenreSerializer,
                          ReviewSerializer, TitleReadSerializer,
                          TitleWriteSerializer)
from reviews.models import Category, Genre, Review, Title
from rest_framework.views import APIView
from user.models import User
from api.utils import send_confirmation_code_to_email


class UserViewSet(APIView):
    """ViewSet для модели User"""
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request, username=None):
        if username is None:
            users_queryset = User.objects.all()
            serializer = UserSerializer(users_queryset, many=True)
            return Response(serializer.data)
        else:

            try:
                user_queryset = User.objects.get(username=username)
            except User.DoesNotExists:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = UserSerializer(user_queryset)
            return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExists:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, username):
        user = self.get_object(username)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            if 'username' in request.data:
                user.username = request.data['username']
                user.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Можно обновлять только поле username'},
                                status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

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
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

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
