from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('robots.txt', views.robots_txt, name='robots_txt'),  # SEO: Robots.txt for search engines
    path('manifest.json', views.manifest_json, name='manifest'),  # PWA: Web app manifest
] 