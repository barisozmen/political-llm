"""
Django management command to automatically create Stripe products and prices
"""
import stripe
from django.core.management.base import BaseCommand
from django.conf import settings
from billing.models import SubscriptionPlan
import logfire


class Command(BaseCommand):
    help = 'Create Stripe products and prices programmatically, then update Django models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate products even if they already exist',
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating Stripe products and prices programmatically...\n')
        
        # Configure Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Define products data
        products_data = [
            {
                'name': 'starter',
                'display_name': 'Starter Plan',
                'description': 'Perfect for getting started with 1,000 monthly credits',
                'price_cents': 1000,  # $10.00 in cents
                'credits': 1000,
            },
            {
                'name': 'pro',
                'display_name': 'Pro Plan',
                'description': 'Best value plan with 3,000 monthly credits for growing businesses',
                'price_cents': 2000,  # $20.00 in cents
                'credits': 3000,
            },
            {
                'name': 'premium',
                'display_name': 'Premium Plan',
                'description': 'Enterprise-grade plan with 5,000 monthly credits',
                'price_cents': 3000,  # $30.00 in cents
                'credits': 5000,
            }
        ]
        
        for product_data in products_data:
            try:
                self.stdout.write(f'Processing {product_data["display_name"]}...')
                
                # Create or find the Stripe product
                stripe_product = self.create_or_get_product(
                    product_data['name'],
                    product_data['display_name'],
                    product_data['description'],
                    options['force']
                )
                
                # Create or find the Stripe price
                stripe_price = self.create_or_get_price(
                    stripe_product.id,
                    product_data['price_cents'],
                    product_data['name'],
                    options['force']
                )
                
                # Update Django model
                self.update_django_plan(
                    product_data['name'],
                    stripe_price.id,
                    product_data['display_name'],
                    product_data['price_cents'] / 100,  # Convert to dollars
                    product_data['credits']
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {product_data["display_name"]}: {stripe_price.id}')
                )
                
                logfire.info("Stripe product and price created", 
                           plan_name=product_data['name'],
                           stripe_product_id=stripe_product.id,
                           stripe_price_id=stripe_price.id)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to create {product_data["display_name"]}: {str(e)}')
                )
                logfire.error("Failed to create Stripe product", 
                            plan_name=product_data['name'],
                            error=str(e))
        
        # Show final status
        self.show_final_status()

    def create_or_get_product(self, name, display_name, description, force=False):
        """Create or retrieve Stripe product"""
        try:
            if not force:
                # Try to find existing product by searching metadata
                products = stripe.Product.list(limit=100)
                for product in products.data:
                    if product.metadata.get('plan_name') == name:
                        self.stdout.write(f'  → Found existing product: {product.id}')
                        return product
            
            # Create new product
            product = stripe.Product.create(
                name=display_name,
                description=description,
                metadata={
                    'plan_name': name,
                    'django_app': 'billing',
                }
            )
            self.stdout.write(f'  → Created new product: {product.id}')
            return product
            
        except stripe.error.StripeError as e:
            raise Exception(f'Stripe product error: {str(e)}')

    def create_or_get_price(self, product_id, price_cents, plan_name, force=False):
        """Create or retrieve Stripe price"""
        try:
            if not force:
                # Try to find existing price by searching metadata
                prices = stripe.Price.list(product=product_id, limit=100)
                for price in prices.data:
                    if (price.metadata.get('plan_name') == plan_name and 
                        price.unit_amount == price_cents and
                        price.recurring and 
                        price.recurring.interval == 'month'):
                        self.stdout.write(f'  → Found existing price: {price.id}')
                        return price
            
            # Create new price
            price = stripe.Price.create(
                product=product_id,
                unit_amount=price_cents,
                currency='usd',
                recurring={'interval': 'month'},
                metadata={
                    'plan_name': plan_name,
                    'django_app': 'billing',
                }
            )
            self.stdout.write(f'  → Created new price: {price.id}')
            return price
            
        except stripe.error.StripeError as e:
            raise Exception(f'Stripe price error: {str(e)}')

    def update_django_plan(self, name, stripe_price_id, display_name, monthly_price, credits):
        """Update or create Django subscription plan"""
        try:
            plan, created = SubscriptionPlan.objects.update_or_create(
                name=name,
                defaults={
                    'display_name': display_name,
                    'stripe_price_id': stripe_price_id,
                    'monthly_price': monthly_price,
                    'credits_per_month': credits,
                    'is_active': True,
                }
            )
            
            action = "Created" if created else "Updated"
            self.stdout.write(f'  → {action} Django plan: {plan.display_name}')
            
        except Exception as e:
            raise Exception(f'Django model error: {str(e)}')

    def show_final_status(self):
        """Show the final status of all plans"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🎉 Stripe products and prices created successfully!'))
        self.stdout.write('\n📋 Current subscription plans:')
        
        for plan in SubscriptionPlan.objects.all().order_by('monthly_price'):
            is_ready = not plan.stripe_price_id.endswith('_placeholder')
            status = "✅ Ready" if is_ready else "⚠️  Needs Setup"
            
            self.stdout.write(
                f'  • {plan.display_name}: ${plan.monthly_price}/month '
                f'({plan.credits_per_month} credits) - {status}'
            )
            self.stdout.write(f'    Price ID: {plan.stripe_price_id}')
        
        # Check if all plans are ready
        all_ready = all(
            not plan.stripe_price_id.endswith('_placeholder') 
            for plan in SubscriptionPlan.objects.all()
        )
        
        if all_ready:
            self.stdout.write('\n🚀 All subscription plans are ready!')
            self.stdout.write('Users can now subscribe to plans on your billing dashboard.')
        else:
            self.stdout.write('\n⚠️  Some plans still need setup. Check the errors above.')
        
        self.stdout.write('\n🔗 Test your billing dashboard at:')
        self.stdout.write('   https://djangotemplate.bozmen.xyz/billing/') 