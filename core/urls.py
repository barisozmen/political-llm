"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.sitemaps.views import sitemap
from authentication.views import CustomLoginView, GoogleOAuthCallbackView, custom_logout_view
from app.sitemaps import StaticPagesSitemap, AuthenticationSitemap

# SEO: Sitemap configuration
sitemaps = {
    'static': StaticPagesSitemap,
    'auth': AuthenticationSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # SEO: XML Sitemap for search engines
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # Custom login view (handles both sign-in and sign-up)
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
    
    # Custom logout view (redirects to home)
    path('accounts/logout/', custom_logout_view, name='account_logout'),
    
    # Redirect signup to login since we handle both
    path('accounts/signup/', RedirectView.as_view(url='/accounts/login/', permanent=False), name='account_signup'),
    
    # Google OAuth callback (must match Google Cloud Console configuration)
    path('accounts/google/login/callback/', GoogleOAuthCallbackView.as_view(), name='google_oauth_callback'),
    
    # Authentication app URLs
    path('auth/', include('authentication.urls')),
    
    # Billing app URLs
    path('billing/', include('billing.urls')),
    
    # Main app URLs
    path('', include('app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
