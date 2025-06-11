from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.conf import settings
from django.urls import reverse
import stripe
import json
import logfire

from .models import SubscriptionPlan, UserSubscription, CreditUsage, BillingHistory
from .services import StripeService


class SubscriptionDashboardView(LoginRequiredMixin, TemplateView):
    """Main subscription dashboard showing current plan and usage"""
    template_name = 'billing/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create user subscription
        subscription, created = UserSubscription.objects.get_or_create(
            user=self.request.user,
            defaults={
                'stripe_customer_id': '',  # Will be set when customer is created
            }
        )
        
        # Get available plans
        plans = SubscriptionPlan.objects.filter(is_active=True)
        
        # Get recent credit usage
        recent_usage = CreditUsage.objects.filter(
            user=self.request.user
        )[:10]
        
        # Get billing history
        billing_history = BillingHistory.objects.filter(
            user=self.request.user
        )[:5]
        
        context.update({
            'subscription': subscription,
            'plans': plans,
            'recent_usage': recent_usage,
            'billing_history': billing_history,
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        })
        
        logfire.info("Subscription dashboard viewed", 
                    user_email=self.request.user.email,
                    has_subscription=bool(subscription.subscription_plan),
                    subscription_status=subscription.status if subscription else None)
        
        return context


@login_required
def create_checkout_session(request):
    """Create Stripe checkout session for subscription"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            
            logfire.info("Checkout session requested", 
                        user_email=request.user.email,
                        plan_id=plan_id)
            
            # Get subscription plan
            plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
            
            # Create checkout session
            success_url = request.build_absolute_uri(
                reverse('billing:subscription_success')
            ) + '?session_id={CHECKOUT_SESSION_ID}'
            
            cancel_url = request.build_absolute_uri(
                reverse('billing:dashboard')
            )
            
            session = StripeService.create_checkout_session(
                user=request.user,
                price_id=plan.stripe_price_id,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            return JsonResponse({'checkout_url': session.url})
            
        except Exception as e:
            logfire.error("Failed to create checkout session", 
                         user_email=request.user.email,
                         error=str(e))
            
            return JsonResponse({
                'error': 'Failed to create checkout session'
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def subscription_success(request):
    """Handle successful subscription"""
    session_id = request.GET.get('session_id')
    
    if session_id:
        try:
            # Retrieve the session to confirm payment
            session = stripe.checkout.Session.retrieve(session_id)
            
            logfire.info("Subscription success page viewed", 
                        user_email=request.user.email,
                        session_id=session_id)
            
            messages.success(
                request,
                'Subscription activated successfully! Welcome to your new plan.'
            )
            
        except Exception as e:
            logfire.error("Error retrieving checkout session", 
                         user_email=request.user.email,
                         session_id=session_id,
                         error=str(e))
            
            messages.warning(
                request,
                'There was an issue confirming your subscription. Please check your dashboard.'
            )
    
    return redirect('billing:dashboard')


@login_required
def create_billing_portal_session(request):
    """Create Stripe billing portal session"""
    try:
        return_url = request.build_absolute_uri(reverse('billing:dashboard'))
        
        session = StripeService.create_billing_portal_session(
            user=request.user,
            return_url=return_url
        )
        
        return redirect(session.url)
        
    except Exception as e:
        logfire.error("Failed to create billing portal session", 
                     user_email=request.user.email,
                     error=str(e))
        
        messages.error(
            request,
            'Unable to access billing portal. Please try again later.'
        )
        return redirect('billing:dashboard')


@login_required
def cancel_subscription(request):
    """Cancel user subscription"""
    if request.method == 'POST':
        try:
            StripeService.cancel_subscription(request.user)
            
            messages.success(
                request,
                'Your subscription will be cancelled at the end of the current billing period.'
            )
            
        except Exception as e:
            logfire.error("Failed to cancel subscription", 
                         user_email=request.user.email,
                         error=str(e))
            
            messages.error(
                request,
                'Unable to cancel subscription. Please try again later.'
            )
    
    return redirect('billing:dashboard')


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        logfire.info("Stripe webhook received", 
                    event_type=event['type'],
                    event_id=event['id'])
        
        # Handle different event types
        if event['type'] == 'customer.subscription.created':
            StripeService.handle_subscription_created(event['data']['object'])
            
        elif event['type'] == 'customer.subscription.updated':
            StripeService.handle_subscription_updated(event['data']['object'])
            
        elif event['type'] == 'invoice.payment_succeeded':
            StripeService.handle_invoice_payment_succeeded(event['data']['object'])
            
        else:
            logfire.info("Unhandled webhook event type", event_type=event['type'])
        
        return HttpResponse(status=200)
        
    except ValueError as e:
        logfire.error("Invalid Stripe webhook payload", error=str(e))
        return HttpResponse(status=400)
        
    except stripe.error.SignatureVerificationError as e:
        logfire.error("Invalid Stripe webhook signature", error=str(e))
        return HttpResponse(status=400)
        
    except Exception as e:
        logfire.error("Error processing Stripe webhook", 
                     error=str(e),
                     event_type=event.get('type') if 'event' in locals() else 'unknown')
        return HttpResponse(status=500)


@login_required
def use_credits(request):
    """Endpoint to use credits (for testing or API integration)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount', 1)
            description = data.get('description', 'Credit usage')
            
            # Get user subscription
            subscription = UserSubscription.objects.get(user=request.user)
            
            if subscription.use_credits(amount, description):
                logfire.info("Credits used successfully", 
                           user_email=request.user.email,
                           amount=amount,
                           remaining=subscription.credits_remaining)
                
                return JsonResponse({
                    'success': True,
                    'credits_remaining': subscription.credits_remaining,
                    'message': f'Used {amount} credits successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Insufficient credits'
                }, status=400)
                
        except UserSubscription.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No subscription found'
            }, status=400)
            
        except Exception as e:
            logfire.error("Failed to use credits", 
                         user_email=request.user.email,
                         error=str(e))
            
            return JsonResponse({
                'success': False,
                'error': 'Failed to use credits'
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
