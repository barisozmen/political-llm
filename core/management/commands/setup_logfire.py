"""
Django management command to set up Logfire configuration
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import logfire


class Command(BaseCommand):
    help = 'Set up Logfire configuration and test logging'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Run test logging to verify Logfire setup',
        )

    def handle(self, *args, **options):
        self.stdout.write('Setting up Logfire...')
        
        # Check if Logfire token is configured
        logfire_token = getattr(settings, 'LOGFIRE_TOKEN', '')
        if not logfire_token:
            self.stdout.write(
                self.style.WARNING(
                    'LOGFIRE_TOKEN not set. Logfire will run in console mode.\n'
                    'To get a token, visit: https://logfire.pydantic.dev/\n'
                    'Then set LOGFIRE_TOKEN in your environment variables.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'LOGFIRE_TOKEN configured: {logfire_token[:8]}...')
            )

        # Test logging if requested
        if options['test']:
            self.stdout.write('Testing Logfire logging...')
            
            logfire.info('Django management command test', 
                        command='setup_logfire',
                        test_mode=True)
            
            logfire.debug('Debug level test log')
            logfire.warning('Warning level test log')
            
            # Test structured logging
            with logfire.span('Test span for Django setup'):
                logfire.info('Inside test span', 
                           data={'key': 'value', 'number': 42})
            
            self.stdout.write(
                self.style.SUCCESS('Test logging completed. Check your Logfire dashboard!')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Logfire setup complete!')
        ) 