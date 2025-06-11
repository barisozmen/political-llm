"""
Stripe service for handling subscription operations
"""
import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserSubscription, SubscriptionPlan, BillingHistory
import logfire

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service class for Stripe operations"""
    
    @staticmethod
    def create_customer(user):
        """Create a Stripe customer for the user"""
        try:
            logfire.info("Creating Stripe customer", user_email=user.email)
            
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}".strip() or user.username,
                metadata={
                    'user_id': user.id,
                    'username': user.username
                }
            )
            
            logfire.info("Stripe customer created successfully", 
                        user_email=user.email,
                        stripe_customer_id=customer.id)
            
            return customer
            
        except Exception as e:
            logfire.error("Failed to create Stripe customer", 
                         user_email=user.email,
                         error=str(e))
            raise
    
    @staticmethod
    def get_or_create_customer(user):
        """Get existing customer or create new one"""
        try:
            subscription = UserSubscription.objects.get(user=user)
            
            # Check if we have a valid customer ID
            if subscription.stripe_customer_id:
                try:
                    customer = stripe.Customer.retrieve(subscription.stripe_customer_id)
                    return customer
                except stripe.error.InvalidRequestError:
                    # Customer doesn't exist in Stripe, create a new one
                    logfire.warning("Stripe customer not found, creating new one", 
                                   user_email=user.email,
                                   old_customer_id=subscription.stripe_customer_id)
                    pass
            
            # Create new customer and update the subscription
            customer = StripeService.create_customer(user)
            subscription.stripe_customer_id = customer.id
            subscription.save()
            
            logfire.info("Updated UserSubscription with new Stripe customer", 
                        user_email=user.email,
                        stripe_customer_id=customer.id)
            
            return customer
            
        except UserSubscription.DoesNotExist:
            # Create both customer and subscription
            customer = StripeService.create_customer(user)
            UserSubscription.objects.create(
                user=user,
                stripe_customer_id=customer.id
            )
            return customer
    
    @staticmethod
    def create_checkout_session(user, price_id, success_url, cancel_url):
        """Create a Stripe checkout session for subscription"""
        try:
            customer = StripeService.get_or_create_customer(user)
            
            logfire.info("Creating Stripe checkout session", 
                        user_email=user.email,
                        price_id=price_id)
            
            session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': user.id
                }
            )
            
            logfire.info("Stripe checkout session created", 
                        user_email=user.email,
                        session_id=session.id)
            
            return session
            
        except Exception as e:
            logfire.error("Failed to create checkout session", 
                         user_email=user.email,
                         error=str(e))
            raise
    
    @staticmethod
    def create_billing_portal_session(user, return_url):
        """Create a Stripe billing portal session"""
        try:
            # Use get_or_create_customer to ensure we have a valid customer
            customer = StripeService.get_or_create_customer(user)
            
            session = stripe.billing_portal.Session.create(
                customer=customer.id,
                return_url=return_url,
            )
            
            logfire.info("Stripe billing portal session created", 
                        user_email=user.email,
                        session_url=session.url)
            
            return session
            
        except Exception as e:
            logfire.error("Failed to create billing portal session", 
                         user_email=user.email,
                         error=str(e))
            raise
    
    @staticmethod
    def handle_subscription_created(subscription_data):
        """Handle subscription.created webhook"""
        try:
            customer_id = subscription_data['customer']
            subscription_id = subscription_data['id']
            
            logfire.info("Processing subscription created webhook", 
                        customer_id=customer_id,
                        subscription_id=subscription_id)
            
            # Get user subscription record
            user_subscription = UserSubscription.objects.get(
                stripe_customer_id=customer_id
            )
            
            # Get subscription plan from price ID
            price_id = subscription_data['items']['data'][0]['price']['id']
            subscription_plan = SubscriptionPlan.objects.get(stripe_price_id=price_id)
            
            # Update subscription
            user_subscription.stripe_subscription_id = subscription_id
            user_subscription.subscription_plan = subscription_plan
            user_subscription.status = subscription_data['status']
            user_subscription.current_period_start = timezone.datetime.fromtimestamp(
                subscription_data['current_period_start'], tz=timezone.utc
            )
            user_subscription.current_period_end = timezone.datetime.fromtimestamp(
                subscription_data['current_period_end'], tz=timezone.utc
            )
            user_subscription.save()
            
            logfire.info("Subscription created successfully", 
                        user_email=user_subscription.user.email,
                        plan=subscription_plan.name)
            
        except Exception as e:
            logfire.error("Failed to process subscription created webhook", 
                         error=str(e),
                         subscription_data=subscription_data)
            raise
    
    @staticmethod
    def handle_subscription_updated(subscription_data):
        """Handle subscription.updated webhook"""
        try:
            subscription_id = subscription_data['id']
            
            logfire.info("Processing subscription updated webhook", 
                        subscription_id=subscription_id)
            
            user_subscription = UserSubscription.objects.get(
                stripe_subscription_id=subscription_id
            )
            
            # Update subscription details
            old_status = user_subscription.status
            user_subscription.status = subscription_data['status']
            user_subscription.current_period_start = timezone.datetime.fromtimestamp(
                subscription_data['current_period_start'], tz=timezone.utc
            )
            user_subscription.current_period_end = timezone.datetime.fromtimestamp(
                subscription_data['current_period_end'], tz=timezone.utc
            )
            
            # Reset credits if new billing period
            if (user_subscription.credits_reset_date is None or 
                user_subscription.current_period_start > user_subscription.credits_reset_date):
                user_subscription.reset_credits()
                
                logfire.info("Credits reset for new billing period", 
                           user_email=user_subscription.user.email)
            
            user_subscription.save()
            
            logfire.info("Subscription updated successfully", 
                        user_email=user_subscription.user.email,
                        old_status=old_status,
                        new_status=user_subscription.status)
            
        except Exception as e:
            logfire.error("Failed to process subscription updated webhook", 
                         error=str(e),
                         subscription_data=subscription_data)
            raise
    
    @staticmethod
    def handle_invoice_payment_succeeded(invoice_data):
        """Handle invoice.payment_succeeded webhook"""
        try:
            customer_id = invoice_data['customer']
            
            logfire.info("Processing invoice payment succeeded webhook", 
                        customer_id=customer_id,
                        invoice_id=invoice_data['id'])
            
            user_subscription = UserSubscription.objects.get(
                stripe_customer_id=customer_id
            )
            
            # Create billing history record
            BillingHistory.objects.create(
                user=user_subscription.user,
                stripe_invoice_id=invoice_data['id'],
                amount_paid=invoice_data['amount_paid'] / 100,  # Convert from cents
                currency=invoice_data['currency'],
                status=invoice_data['status'],
                billing_reason=invoice_data.get('billing_reason'),
                invoice_url=invoice_data.get('hosted_invoice_url')
            )
            
            logfire.info("Invoice payment recorded", 
                        user_email=user_subscription.user.email,
                        amount=invoice_data['amount_paid'] / 100)
            
        except Exception as e:
            logfire.error("Failed to process invoice payment webhook", 
                         error=str(e),
                         invoice_data=invoice_data)
            raise
    
    @staticmethod
    def cancel_subscription(user):
        """Cancel user's subscription"""
        try:
            user_subscription = UserSubscription.objects.get(user=user)
            
            if user_subscription.stripe_subscription_id:
                stripe.Subscription.modify(
                    user_subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                
                logfire.info("Subscription cancelled", 
                           user_email=user.email,
                           subscription_id=user_subscription.stripe_subscription_id)
            
        except Exception as e:
            logfire.error("Failed to cancel subscription", 
                         user_email=user.email,
                         error=str(e))
            raise 