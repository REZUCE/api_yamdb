from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from api.filters import FilterTitle
from api.mixins import ModelMixinSet
from api.permissions import (IsAdminUserOrReadOnly)
from api.serializers import (CategorySerializer, GenreSerializer,
                             TitleReadSerializer, TitleWriteSerializer)
from reviews.models import Category, Genre, Title


class CategoryViewSet(ModelMixinSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


# class TitleViewSet(viewsets.ModelViewSet):
#     queryset = Title.objects.annotate(
#         rating=Avg('reviews__score'),
#     ).all()
#     permission_classes = (IsAdminUserOrReadOnly,)
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = FilterTitle
#
#     def get_serializer_class(self):
#         if self.action in ('list', 'retrieve'):
#             return TitleReadSerializer
#         return TitleWriteSerializer
