from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (CategoryViewSet, GenreViewSet,
                    TitleViewSet, ReviewViewSet,
                    CommentsViewSet, )
from user.views import (UserViewSet, UserMeViewSet, )
from user.urls_auth import urls_auth
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='titles_reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='reviews_comments'
)
urlpatterns = [
    path('v1/', include(urls_auth)),
    path('v1/users/me/', UserMeViewSet.as_view(), name='user_me'),
    path('v1/', include(router.urls))
]
