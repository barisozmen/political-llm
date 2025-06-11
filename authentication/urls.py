from django.urls import path
from django.contrib.auth.views import LoginView
from sesame.views import LoginView as SesameLoginView
from . import views

app_name = 'authentication'

urlpatterns = [
    path('magic-link/', views.MagicLinkView.as_view(), name='magic_link'),
    path('magic-link-login/', SesameLoginView.as_view(), name='magic_link_login'),
    path('magic-link-signup/', views.MagicLinkSignupView.as_view(), name='magic_link_signup'),
    path('magic-link/sent/', views.MagicLinkSentView.as_view(), name='magic_link_sent'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('google-login/', views.GoogleOAuthRedirectView.as_view(), name='google_login'),
    path('google-callback/', views.GoogleOAuthCallbackView.as_view(), name='google_callback'),
] 