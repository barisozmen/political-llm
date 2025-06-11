from django.core.management.base import BaseCommand
from core import settings

import subprocess
import os
import sys
import fire


class DeploymentCommands:
    """Deployment commands for different environments using Fire CLI."""
    
    def __init__(self):
        # Constants
        self.DIR_ROOT_NAME = settings.BASE_DIR
        self.SERVER = "root@64.225.56.62"
        self.CANARY_PATH = f"{self.DIR_ROOT_NAME}/"
        self.PROD_PATH = f"{self.DIR_ROOT_NAME}_prod/"
        self.CANARY_APP_NAME = f"{str(self.DIR_ROOT_NAME).split('/')[-1]}"
        self.PROD_APP_NAME = f"{str(self.DIR_ROOT_NAME).split('/')[-1]}_prod"

        self.RSYNC_BASE = (
            "rsync -ravz --delete "
            "--exclude-from='.gitignore' "
            "--exclude '*.pyc' "
            "--exclude '__pycache__' "
            "--exclude 'media/*' "
            "--exclude 'static/*' "
            "--exclude 'venv' "
            "--exclude '.env' "
            "--exclude '*.sqlite3'"
        )

        

    def setup_ssh(self):
        """Set up SSH agent and add SSH key."""
        print("Setting up SSH agent...")
        try:
            subprocess.run(["eval", "$(ssh-agent -s)"], check=True, shell=True)
            print("Adding SSH key...")
            subprocess.run(["ssh-add", "~/.ssh/id_rsa"], check=True)
            print("SSH setup completed successfully.")
        except subprocess.CalledProcessError:
            print("SSH setup failed")
            sys.exit(1)

    def run_command(self, command):
        """Run a shell command and handle errors."""
        print(f"Running command: {command}")
        try:
            subprocess.run(command, check=True, shell=True)
            print("Command completed successfully.")
        except subprocess.CalledProcessError:
            print("Command failed")
            sys.exit(1)

    def _get_pm2_commands(self, app_name, with_migrations=False):
        """Get PM2 commands with optional migrations."""
        migration_command = "python3 manage.py makemigrations; python3 manage.py migrate;"
        pm2_commands_base = "python3 manage.py collectstatic --noinput"
        
        if with_migrations:
            pm2_commands_base = f"{migration_command} {pm2_commands_base}"
        
        return f'{pm2_commands_base}; pm2 delete {app_name} --silent; pm2 start "python3 manage.py run_daphne" --name {app_name}; pm2 save'

    def lc(self, migrations=False):
        """Deploy from local to canary environment.
        
        Args:
            migrations (bool): Run migrations during deployment. Defaults to False.
        """
        self.setup_ssh()
        print("Deploying from local to canary environment...")
        self.run_command(f"{self.RSYNC_BASE} . {self.SERVER}:{self.CANARY_PATH}")
        pm2_commands = self._get_pm2_commands(self.CANARY_APP_NAME, migrations)
        self.run_command(f'ssh {self.SERVER} "cd {self.CANARY_PATH} && {pm2_commands}"')
        print("Deployment to canary environment completed.")

    def lp(self, migrations=False):
        """Deploy from local to production environment.
        
        Args:
            migrations (bool): Run migrations during deployment. Defaults to False.
        """
        self.setup_ssh()
        print("Deploying from local to production environment...")
        self.run_command(f"{self.RSYNC_BASE} . {self.SERVER}:{self.PROD_PATH}")
        pm2_commands = self._get_pm2_commands(self.PROD_APP_NAME, migrations)
        self.run_command(f'ssh {self.SERVER} "cd {self.PROD_PATH} && {pm2_commands}"')
        print("Deployment to production environment completed.")

    def cp(self, migrations=False):
        """Deploy from canary to production environment.
        
        Args:
            migrations (bool): Run migrations during deployment. Defaults to False.
        """
        print("Deploying from canary to production environment...")
        self.run_command(f"sudo rsync {self.RSYNC_BASE} {self.CANARY_PATH} {self.PROD_PATH}")
        pm2_commands = self._get_pm2_commands(self.PROD_APP_NAME, migrations)
        self.run_command(f"cd {self.PROD_PATH} && {pm2_commands}")
        print("Deployment from canary to production completed.")

    def cc(self, migrations=False):
        """Build on canary environment.
        
        Args:
            migrations (bool): Run migrations during deployment. Defaults to False.
        """
        print("Building on canary environment...")
        pm2_commands = self._get_pm2_commands(self.CANARY_APP_NAME, migrations)
        self.run_command(f"cd {self.CANARY_PATH} && {pm2_commands}")
        print("Build on canary environment completed.")

    def pp(self, migrations=False):
        """Deploy from production to production (local PM2 commands only).
        
        Args:
            migrations (bool): Run migrations during deployment. Defaults to False.
        """
        print("Restarting production environment...")
        pm2_commands = self._get_pm2_commands(self.PROD_APP_NAME, migrations)
        self.run_command(f"cd {self.PROD_PATH} && {pm2_commands}")
        print("Production environment restarted.")


class Command(BaseCommand):
    help = "Deploy application to different environments using Fire CLI"

    def add_arguments(self, parser):
        # Keep the parser for Django compatibility, but we'll use Fire instead
        parser.add_argument(
            "fire_args",
            nargs="*",
            help="Arguments to pass to Fire CLI (e.g., 'lc --migrations=True')",
        )

    def handle(self, *args, **options):
        # Extract fire arguments from Django command
        fire_args = options.get("fire_args", [])
        
        if not fire_args:
            print("Usage examples:")
            print("  python manage.py deploy lc                    # Deploy local to canary")
            print("  python manage.py deploy lc --migrations=True  # Deploy local to canary with migrations")
            print("  python manage.py deploy lp                    # Deploy local to production")
            print("  python manage.py deploy cp                    # Deploy canary to production")
            print("  python manage.py deploy cc                    # Build on canary")
            print("  python manage.py deploy pp                    # Restart production")
            print("  python manage.py deploy -- --help             # Show Fire help")
            return

        # Create deployment commands instance and use Fire
        deployment = DeploymentCommands()
        
        # Use Fire to parse and execute the command
        try:
            fire.Fire(deployment, command=fire_args)
        except SystemExit:
            # Fire calls sys.exit, which we catch to prevent Django from showing errors
            pass
