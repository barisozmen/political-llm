from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Subscription dashboard
    path('', views.SubscriptionDashboardView.as_view(), name='dashboard'),
    
    # Stripe checkout
    path('checkout/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.subscription_success, name='subscription_success'),
    
    # Subscription management
    path('billing-portal/', views.create_billing_portal_session, name='billing_portal'),
    path('cancel/', views.cancel_subscription, name='cancel_subscription'),
    
    # Credit usage (API endpoint)
    path('use-credits/', views.use_credits, name='use_credits'),
    
    # Stripe webhooks
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
] 