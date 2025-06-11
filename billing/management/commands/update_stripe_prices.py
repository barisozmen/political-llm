"""
Django management command to update Stripe price IDs for subscription plans
"""
from django.core.management.base import BaseCommand
from billing.models import SubscriptionPlan
import logfire


class Command(BaseCommand):
    help = 'Update Stripe price IDs for subscription plans'

    def add_arguments(self, parser):
        parser.add_argument(
            '--starter-price-id',
            type=str,
            help='Stripe price ID for Starter plan ($10/month)',
        )
        parser.add_argument(
            '--pro-price-id',
            type=str,
            help='Stripe price ID for Pro plan ($20/month)',
        )
        parser.add_argument(
            '--premium-price-id',
            type=str,
            help='Stripe price ID for Premium plan ($30/month)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Updating Stripe price IDs...\n')
        
        # Update Starter Plan
        if options['starter_price_id']:
            try:
                starter = SubscriptionPlan.objects.get(name='starter')
                starter.stripe_price_id = options['starter_price_id']
                starter.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated Starter Plan: {options["starter_price_id"]}')
                )
                logfire.info("Stripe price ID updated", 
                           plan="starter", 
                           price_id=options['starter_price_id'])
            except SubscriptionPlan.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR('✗ Starter Plan not found')
                )

        # Update Pro Plan
        if options['pro_price_id']:
            try:
                pro = SubscriptionPlan.objects.get(name='pro')
                pro.stripe_price_id = options['pro_price_id']
                pro.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated Pro Plan: {options["pro_price_id"]}')
                )
                logfire.info("Stripe price ID updated", 
                           plan="pro", 
                           price_id=options['pro_price_id'])
            except SubscriptionPlan.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR('✗ Pro Plan not found')
                )

        # Update Premium Plan
        if options['premium_price_id']:
            try:
                premium = SubscriptionPlan.objects.get(name='premium')
                premium.stripe_price_id = options['premium_price_id']
                premium.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated Premium Plan: {options["premium_price_id"]}')
                )
                logfire.info("Stripe price ID updated", 
                           plan="premium", 
                           price_id=options['premium_price_id'])
            except SubscriptionPlan.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR('✗ Premium Plan not found')
                )

        # Show current status
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Current Stripe Price IDs:')
        for plan in SubscriptionPlan.objects.all().order_by('monthly_price'):
            status = "✓ Ready" if not plan.stripe_price_id.endswith('_placeholder') else "⚠ Needs Update"
            self.stdout.write(f'  {plan.display_name}: {plan.stripe_price_id} ({status})')

        self.stdout.write('\n📋 Usage example:')
        self.stdout.write('python manage.py update_stripe_prices \\')
        self.stdout.write('  --starter-price-id price_1ABC123... \\')
        self.stdout.write('  --pro-price-id price_1DEF456... \\')
        self.stdout.write('  --premium-price-id price_1GHI789...') 