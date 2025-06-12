from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'app/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Welcome to Political God LLM'
        return context


class AboutView(TemplateView):
    """About page view"""
    template_name = 'app/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'About - Political God LLM'
        return context


class PrivacyView(TemplateView):
    """Privacy Policy page view"""
    template_name = 'app/privacy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Privacy Policy - Political God LLM'
        return context


class TermsView(TemplateView):
    """Terms of Service page view"""
    template_name = 'app/terms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Terms of Service - Political God LLM'
        return context


@require_GET
@cache_page(60 * 60 * 24)  # Cache for 24 hours
def robots_txt(request):
    """Generate robots.txt file for search engines"""
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "# Disallow private areas",
        "Disallow: /admin/",
        "Disallow: /auth/magic-link/",
        "Disallow: /auth/profile/",
        "Disallow: /political-god/",
        "",
        "# Allow important pages",
        "Allow: /",
        "Allow: /info/about/",
        "Allow: /info/privacy/",
        "Allow: /info/terms/",
        "Allow: /accounts/login/",
        "Allow: /accounts/signup/",
        "",
        "# Sitemap",
        f"Sitemap: https://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


@require_GET
@cache_page(60 * 60 * 24)  # Cache for 24 hours
def manifest_json(request):
    """Generate web app manifest for PWA features"""
    manifest = {
        "name": "Political God LLM",
        "short_name": "PoliticalLLM",
        "description": "AI-powered legal framework generator for creating laws and constitutions",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#667eea",
        "theme_color": "#667eea",
        "orientation": "portrait-primary",
        "categories": ["productivity", "legal", "ai"],
        "lang": "en-US",
        "icons": [
            {
                "src": "/static/favicon-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "/static/favicon-512x512.png", 
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ],
        "screenshots": [
            {
                "src": "/static/images/screenshot-desktop.png",
                "sizes": "1280x720",
                "type": "image/png",
                "form_factor": "wide"
            },
            {
                "src": "/static/images/screenshot-mobile.png",
                "sizes": "390x844",
                "type": "image/png",
                "form_factor": "narrow"
            }
        ]
    }
    return JsonResponse(manifest)
