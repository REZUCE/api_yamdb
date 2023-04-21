from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (CategoryViewSet, GenreViewSet,
                    TitleViewSet, UserViewSet,
                    UserMeViewSet, SignupView,
                    ReviewViewSet, CommentsViewSet, )

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(r'titles/?P<title_id>\d+/reviews/', ReviewViewSet, basename='reviews')
router.register(r'titles/?P<title_id>\d+/reviews/?P<title_id>\d+/', CommentsViewSet, basename='comments')
urlpatterns = [
    # path('v1/auth/token/', )
    path('v1/auth/signup/', SignupView.as_view(), name='signup'),
    path('v1/users/me/', UserMeViewSet.as_view(), name='user_me'),
    path('v1/', include(router.urls))
]
