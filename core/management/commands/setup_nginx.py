"""
Django management command for setting up nginx configuration.
"""

from sysconfig import get_path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
import sys
import shutil
import subprocess
from pathlib import Path
import fire


class NginxConfSetup:
    """Simple nginx configuration setup using python-fire."""
    
    def __init__(self):
        self.sites_available = Path("/etc/nginx/sites-available")
        self.sites_enabled = Path("/etc/nginx/sites-enabled")
    
    def generate_simple_nginx_config(self, 
                                   domain=settings.SITE_DOMAIN, 
                                   port=settings.SERVER_PORT,
                                   project_path=settings.BASE_DIR):
        """Generate a simple nginx configuration."""
        config = f"""server {{
    server_name {domain};

    location / {{
        proxy_pass http://localhost:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /static/ {{
        alias {project_path}/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }}
}}"""
        return config
    
    def check_permissions(self):
        """Check if running with sufficient permissions."""
        if os.geteuid() != 0:
            print("❌ This script requires root privileges.")
            print("   Please run with sudo")
            return False
        return True
    
    def check_nginx_installed(self):
        """Check if nginx is installed."""
        try:
            subprocess.run(["nginx", "-v"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Nginx is not installed or not in PATH.")
            print("   Install nginx first: sudo apt update && sudo apt install nginx")
            return False
    
    def backup_existing_config(self, config_name):
        """Backup existing configuration if it exists."""
        config_path = self.sites_available / config_name
        if config_path.exists():
            backup_path = config_path.with_suffix(f"{config_path.suffix}.backup")
            shutil.copy2(config_path, backup_path)
            print(f"📁 Backed up existing config to {backup_path}")
    
    def setup(self, 
              project_name=settings.PROJECT_NAME,
              domain=settings.SITE_DOMAIN, 
              port=settings.SERVER_PORT, 
              project_path=settings.BASE_DIR,
              dry_run=False):
        """
        Set up nginx configuration with simple settings.
        
        Args:
            project_name: Name of the project (default: dictionary)
            domain: Domain name (default: dictionary.bozmen.xyz)
            port: Application port (default: 8302)
            project_path: Project directory path (default: /var/www/dictionary)
            dry_run: Show what would be done without making changes (default: False)
        """
        
        if dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            print(f"   Would setup nginx for project: {project_name}")
            print(f"   Would use domain: {domain}")
            print(f"   Would use port: {port}")
            print(f"   Would use project path: {project_path}")
            print(f"   Would write config to: /etc/nginx/sites-available/{project_name}")
            print(f"   Would create symlink in: /etc/nginx/sites-enabled/{project_name}")
            print("\nGenerated config would be:")
            print("-" * 50)
            print(self.generate_simple_nginx_config(domain, port, project_path))
            print("-" * 50)
            return
        
        print(f"🚀 Setting up nginx configuration for {project_name}")
        print(f"   Domain: {domain}")
        print(f"   Port: {port}")
        print(f"   Project Path: {project_path}")
        print()
        
        # Check prerequisites
        if not self.check_permissions():
            return False
            
        if not self.check_nginx_installed():
            return False
        
        # Backup existing config
        self.backup_existing_config(project_name)
        
        # Generate and write configuration
        config_content = self.generate_simple_nginx_config(domain, port, project_path)
        config_path = project_path / 'nginx.conf'
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Generated and wrote nginx config to {config_path}")
        
        # Create symlink
        symlink_path = self.sites_enabled / project_name
        
        # Remove existing symlink if it exists
        if symlink_path.exists() or symlink_path.is_symlink():
            symlink_path.unlink()
            print(f"🔄 Removed existing symlink at {symlink_path}")
        
        # Create new symlink
        symlink_path.symlink_to(config_path)
        print(f"✅ Created symlink: {symlink_path} -> {config_path}")
        
        # Test configuration
        try:
            subprocess.run(["nginx", "-t"], capture_output=True, text=True, check=True)
            print("✅ Nginx configuration test passed")
        except subprocess.CalledProcessError as e:
            print("❌ Nginx configuration test failed:")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            return False
        
        # Reload nginx
        try:
            subprocess.run(["systemctl", "reload", "nginx"], check=True)
            print("✅ Nginx reloaded successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to reload nginx: {e}")
            return False
        
        # Enable SSL by certbot
        subprocess.run(["sudo", "certbot", "--nginx", "-d", domain], check=True)
        
        print(f"\n🎉 Nginx setup completed successfully!")
        print(f"   Your site should now be available at: http://{domain}")
        print(f"\n📋 Next steps:")
        print(f"   1. Make sure your Django application is running on port {port}")
        print(f"   2. Consider setting up SSL with certbot for HTTPS")
        print(f"   3. Test the configuration by visiting your domain")
        
        return True


class Command(BaseCommand):
    help = 'Set up and link nginx configuration to sites-enabled directory using python-fire'

    def add_arguments(self, parser):
        # No arguments needed - fire will handle everything
        pass

    def handle(self, *args, **options):
        """Run the nginx setup using python-fire."""
        print("🔧 Nginx Configuration Setup Tool")
        print("📖 Usage examples:")
        print("   # Basic setup with defaults:")
        print("   sudo python manage.py setup_nginx_conf")
        print()
        print("   # Custom domain and port:")
        print("   fire.Fire(NginxConfSetup).setup --domain=mysite.com --port=8000")
        print()
        print("   # Dry run to see what would be done:")
        print("   fire.Fire(NginxConfSetup).setup --dry_run=True")
        print()
        print("   # Full customization:")
        print("   fire.Fire(NginxConfSetup).setup --project_name=myproject --domain=mysite.com --port=8000 --project_path=/var/www/myproject")
        print()
        
        # Initialize and run with fire
        nginx_setup = NginxConfSetup()
        
        # If no additional arguments, run with defaults
        if len(sys.argv) <= 3:  # manage.py, setup_nginx_conf, and maybe some django args
            return nginx_setup.setup()
        
        # Otherwise let fire handle the arguments
        try:
            fire.Fire(nginx_setup)
        except SystemExit:
            # Fire calls sys.exit, we want to handle it gracefully in Django
            pass 