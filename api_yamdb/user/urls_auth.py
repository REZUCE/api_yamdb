from django.urls import path
from .views import GetTokenView, SignupView

urls_auth = [
    path('auth/token/', GetTokenView.as_view(), name='get_token'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
]