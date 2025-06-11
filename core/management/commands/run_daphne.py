from django.core.management.base import BaseCommand
from daphne.server import Server
import os
from django.utils.module_loading import import_string
from core import settings


class Command(BaseCommand):
    help = "Run the Daphne server on a specified port."

    def add_arguments(self, parser):
        parser.add_argument(
            "--port",
            type=int,
            default=settings.SERVER_PORT,
            help="Specify the port for Daphne to listen on.",
        )
        

    def handle(self, *args, **options):
        PORT = options["port"]
        INTERFACE = "127.0.0.1"
        APPLICATION = "core.asgi.application"
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

        # Import the ASGI application
        application = import_string(APPLICATION)

        # Print startup information
        self.stdout.write(
            self.style.SUCCESS(f"Starting Daphne server on port {PORT}...")
        )
        self.stdout.write(self.style.SUCCESS(f"Using ASGI application: {APPLICATION}"))
        self.stdout.write(self.style.SUCCESS(f"Interface: {INTERFACE}"))

        # Start Daphne server with the imported application
        Server(
            application=application,
            endpoints=[f"tcp:port={PORT}:interface={INTERFACE}"],
        ).run()
        
