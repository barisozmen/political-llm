from django.conf import settings


def seo_context(request):
    """
    Context processor to provide SEO and site information
    across all templates
    """
    return {
        'site': {
            'name': 'Django Auth System',
            'domain': 'djangotemplate.bozmen.xyz',
            'description': 'Modern Django authentication system with Google OAuth, magic links, and Stripe integration',
            'keywords': 'Django authentication, passwordless login, magic links, Google OAuth, secure authentication',
            'author': 'Django Auth System',
            'twitter': '@DjangoAuth',
            'facebook': 'DjangoAuth',
            'og_image': 'https://djangotemplate.bozmen.xyz/static/images/django-auth-og.jpg',
            'logo': 'https://djangotemplate.bozmen.xyz/static/images/logo.png',
        },
        'seo': {
            'google_analytics_id': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
            'google_site_verification': getattr(settings, 'GOOGLE_SITE_VERIFICATION', ''),
            'facebook_app_id': getattr(settings, 'FACEBOOK_APP_ID', ''),
        }
    } 