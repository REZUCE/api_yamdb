from rest_framework.routers import DefaultRouter
from django.urls import path, include
from api.views import (CategoryViewSet, GenreViewSet,
                       TitleViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')

urlpatterns = [

    path('', include(router.urls)),
]
