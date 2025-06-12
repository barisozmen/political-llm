from django.core.management.base import BaseCommand
from political_god.models import LawCategory
from billing.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Set up initial data for Political God LLM'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Political God LLM...'))
        
        # Create law categories
        categories = [
            {
                'name': 'Constitutional',
                'description': 'Fundamental laws and constitutional frameworks',
                'icon': 'fas fa-scroll'
            },
            {
                'name': 'Economic',
                'description': 'Economic policies, taxation, and financial regulations',
                'icon': 'fas fa-chart-line'
            },
            {
                'name': 'Technology',
                'description': 'Technology governance, AI, data privacy, and digital rights',
                'icon': 'fas fa-microchip'
            },
            {
                'name': 'Environmental',
                'description': 'Environmental protection and sustainability laws',
                'icon': 'fas fa-leaf'
            },
            {
                'name': 'Social',
                'description': 'Social policies, education, healthcare, and welfare',
                'icon': 'fas fa-users'
            },
            {
                'name': 'Security',
                'description': 'Security, defense, and law enforcement',
                'icon': 'fas fa-shield-alt'
            },
            {
                'name': 'Immigration',
                'description': 'Immigration, citizenship, and residency laws',
                'icon': 'fas fa-passport'
            },
            {
                'name': 'Trade',
                'description': 'Trade, commerce, and business regulations',
                'icon': 'fas fa-handshake'
            },
            {
                'name': 'Infrastructure',
                'description': 'Infrastructure, transportation, and urban planning',
                'icon': 'fas fa-city'
            },
            {
                'name': 'Governance',
                'description': 'Administrative procedures and governmental operations',
                'icon': 'fas fa-university'
            }
        ]
        
        created_categories = 0
        for cat_data in categories:
            category, created = LawCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon']
                }
            )
            if created:
                created_categories += 1
                self.stdout.write(f'  ✓ Created category: {category.name}')
            else:
                self.stdout.write(f'  - Category already exists: {category.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_categories} law categories')
        )
        
        # Update subscription plans for Political God LLM
        plans = [
            {
                'name': 'starter',
                'display_name': 'Starter Plan',
                'monthly_price': 10.00,
                'credits_per_month': 1000,
                'stripe_price_id': 'price_starter_political_god'
            },
            {
                'name': 'pro',
                'display_name': 'Pro Plan',
                'monthly_price': 50.00,
                'credits_per_month': 5000,
                'stripe_price_id': 'price_pro_political_god'
            },
            {
                'name': 'premium',
                'display_name': 'Premium Plan',
                'monthly_price': 100.00,
                'credits_per_month': 10000,
                'stripe_price_id': 'price_premium_political_god'
            }
        ]
        
        created_plans = 0
        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults={
                    'display_name': plan_data['display_name'],
                    'monthly_price': plan_data['monthly_price'],
                    'credits_per_month': plan_data['credits_per_month'],
                    'stripe_price_id': plan_data['stripe_price_id']
                }
            )
            if created:
                created_plans += 1
                self.stdout.write(f'  ✓ Created plan: {plan.display_name}')
            else:
                # Update existing plan
                plan.display_name = plan_data['display_name']
                plan.monthly_price = plan_data['monthly_price']
                plan.credits_per_month = plan_data['credits_per_month']
                plan.save()
                self.stdout.write(f'  ↻ Updated plan: {plan.display_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully set up {len(plans)} subscription plans')
        )
        
        self.stdout.write(
            self.style.SUCCESS('🏛️ Political God LLM setup complete!')
        )
        self.stdout.write(
            self.style.WARNING('Next steps:')
        )
        self.stdout.write('  1. Set up your OpenAI API key in environment variables')
        self.stdout.write('  2. Configure Stripe for payments')
        self.stdout.write('  3. Create a superuser: python manage.py createsuperuser')
        self.stdout.write('  4. Start the server: python manage.py runserver') 