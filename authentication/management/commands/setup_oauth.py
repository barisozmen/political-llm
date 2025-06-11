from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Set up Google OAuth application for development'

    def handle(self, *args, **options):
        # Get or create the default site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': '127.0.0.1:8000',
                'name': 'Django Auth Template'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created site: {site.domain}')
            )
        
        # Create Google OAuth app for development
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth (Development)',
                'client_id': 'your-google-client-id',
                'secret': 'your-google-client-secret',
            }
        )
        
        if created:
            # Add the site to the app
            google_app.sites.add(site)
            self.stdout.write(
                self.style.SUCCESS('Created Google OAuth application (development mode)')
            )
            self.stdout.write(
                self.style.WARNING('⚠️  Remember to update the client_id and secret in Django admin!')
            )
            self.stdout.write(
                self.style.WARNING('   Go to: http://127.0.0.1:8000/admin/socialaccount/socialapp/')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Google OAuth application already exists')
            )
            # Ensure the app is associated with the site
            if site not in google_app.sites.all():
                google_app.sites.add(site)
                self.stdout.write(
                    self.style.SUCCESS(f'Added site {site.domain} to Google OAuth app')
                ) 