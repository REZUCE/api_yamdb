from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.urls import urls_auth
from user.views import UserViewSet

from .views import CategoryViewSet
from .views import CommentsViewSet
from .views import GenreViewSet
from .views import ReviewViewSet
from .views import TitleViewSet

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='titles_reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='reviews_comments'
)
urlpatterns = [
    path('v1/', include(urls_auth)),
    path('v1/', include(router_v1.urls))
]
