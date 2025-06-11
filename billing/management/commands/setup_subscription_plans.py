"""
Django management command to set up subscription plans
"""
from django.core.management.base import BaseCommand
from billing.models import SubscriptionPlan
import logfire


class Command(BaseCommand):
    help = 'Set up subscription plans with Stripe price IDs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing plans if they exist',
        )

    def handle(self, *args, **options):
        self.stdout.write('Setting up subscription plans...')
        
        # Define the plans as specified in requirements
        plans_data = [
            {
                'name': 'starter',
                'display_name': 'Starter Plan',
                'monthly_price': 10.00,
                'credits_per_month': 1000,
                'stripe_price_id': 'price_starter_placeholder',  # Replace with actual Stripe price ID
            },
            {
                'name': 'pro',
                'display_name': 'Pro Plan (Best Value)',
                'monthly_price': 20.00,
                'credits_per_month': 3000,
                'stripe_price_id': 'price_pro_placeholder',  # Replace with actual Stripe price ID
            },
            {
                'name': 'premium',
                'display_name': 'Premium Plan',
                'monthly_price': 30.00,
                'credits_per_month': 5000,
                'stripe_price_id': 'price_premium_placeholder',  # Replace with actual Stripe price ID
            }
        ]
        
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults={
                    'display_name': plan_data['display_name'],
                    'monthly_price': plan_data['monthly_price'],
                    'credits_per_month': plan_data['credits_per_month'],
                    'stripe_price_id': plan_data['stripe_price_id'],
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created plan: {plan.display_name}')
                )
                logfire.info("Subscription plan created", 
                           plan_name=plan.name,
                           display_name=plan.display_name,
                           price=float(plan.monthly_price))
            else:
                if options['update']:
                    # Update existing plan
                    plan.display_name = plan_data['display_name']
                    plan.monthly_price = plan_data['monthly_price']
                    plan.credits_per_month = plan_data['credits_per_month']
                    plan.stripe_price_id = plan_data['stripe_price_id']
                    plan.save()
                    
                    self.stdout.write(
                        self.style.WARNING(f'⟳ Updated existing plan: {plan.display_name}')
                    )
                    logfire.info("Subscription plan updated", 
                               plan_name=plan.name,
                               display_name=plan.display_name,
                               price=float(plan.monthly_price))
                else:
                    self.stdout.write(
                        self.style.WARNING(f'- Plan already exists: {plan.display_name}')
                    )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Subscription plans setup complete!'))
        self.stdout.write('\n📋 Current plans:')
        
        for plan in SubscriptionPlan.objects.all().order_by('monthly_price'):
            status = "✓ Active" if plan.is_active else "✗ Inactive"
            self.stdout.write(
                f'  • {plan.display_name}: ${plan.monthly_price}/month '
                f'({plan.credits_per_month} credits) - {status}'
            )
        
        self.stdout.write('\n🔧 Next steps:')
        self.stdout.write('1. Create products and prices in your Stripe Dashboard')
        self.stdout.write('2. Update the stripe_price_id for each plan in Django admin')
        self.stdout.write('3. Set up Stripe webhook endpoint: /billing/webhook/')
        self.stdout.write('4. Configure STRIPE_* environment variables')
        self.stdout.write('\n📖 Documentation: https://stripe.com/docs/billing/subscriptions') 