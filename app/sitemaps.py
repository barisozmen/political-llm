from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticPagesSitemap(Sitemap):
    """Sitemap for static pages"""
    changefreq = 'monthly'
    priority = 0.8
    protocol = 'https'  # Use HTTPS for production

    def items(self):
        # Return list of URL names for static pages
        return [
            'app:home',
            'app:about', 
            'app:privacy',
            'app:terms',
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        # For static pages, you might want to return a fixed date
        # or implement logic to track when pages were last updated
        from datetime import datetime
        return datetime.now()


class AuthenticationSitemap(Sitemap):
    """Sitemap for authentication pages"""
    changefreq = 'yearly'
    priority = 0.6
    protocol = 'https'

    def items(self):
        return [
            'account_login',
            'account_signup',
        ]

    def location(self, item):
        return reverse(item) 