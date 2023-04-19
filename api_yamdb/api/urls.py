from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (CategoryViewSet, GenreViewSet,
                       TitleViewSet, UserViewSet) #SignupView

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/users/', UserViewSet.as_view()),
    path('v1/users/<str:username>/', UserViewSet.as_view()),
    # path('v1/auth/signup/', SignupView.as_view(), name='signup'),
    path('v1/', include(router.urls))
]
