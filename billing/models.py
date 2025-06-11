from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import uuid


class SubscriptionPlan(models.Model):
    """Defines the available subscription plans"""
    PLAN_CHOICES = [
        ('starter', 'Starter'),
        ('pro', 'Pro'),
        ('premium', 'Premium'),
    ]
    
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    stripe_price_id = models.CharField(max_length=100, unique=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    credits_per_month = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['monthly_price']
    
    def __str__(self):
        return f"{self.display_name} - ${self.monthly_price}/month ({self.credits_per_month} credits)"


class UserSubscription(models.Model):
    """Tracks user subscription details"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('past_due', 'Past Due'),
        ('unpaid', 'Unpaid'),
        ('incomplete', 'Incomplete'),
        ('incomplete_expired', 'Incomplete Expired'),
        ('trialing', 'Trialing'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    stripe_customer_id = models.CharField(max_length=100, unique=True)
    stripe_subscription_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='incomplete')
    
    # Billing cycle information
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    
    # Credit tracking
    credits_used = models.IntegerField(default=0)
    credits_reset_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.subscription_plan.display_name if self.subscription_plan else 'No Plan'}"
    
    @property
    def credits_remaining(self):
        """Calculate remaining credits for current billing cycle"""
        if not self.subscription_plan:
            return 0
        return max(0, self.subscription_plan.credits_per_month - self.credits_used)
    
    @property
    def usage_percentage(self):
        """Calculate percentage of credits used"""
        if not self.subscription_plan or self.subscription_plan.credits_per_month == 0:
            return 0
        return min(100, (self.credits_used / self.subscription_plan.credits_per_month) * 100)
    
    @property
    def is_active(self):
        """Check if subscription is active"""
        return self.status == 'active'
    
    def reset_credits(self):
        """Reset credits for new billing cycle"""
        self.credits_used = 0
        self.credits_reset_date = timezone.now()
        self.save()
    
    def use_credits(self, amount, description="Credit usage"):
        """Use credits and track usage"""
        if self.credits_remaining >= amount:
            self.credits_used += amount
            self.save()
            
            # Create usage record
            CreditUsage.objects.create(
                user=self.user,
                subscription=self,
                amount=amount,
                description=description,
                billing_period_start=self.current_period_start,
                billing_period_end=self.current_period_end
            )
            return True
        return False


class CreditUsage(models.Model):
    """Tracks individual credit usage events"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_usage')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='usage_records')
    amount = models.IntegerField()
    description = models.CharField(max_length=255)
    billing_period_start = models.DateTimeField()
    billing_period_end = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} credits - {self.description}"


class BillingHistory(models.Model):
    """Tracks billing events and invoice history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='billing_history')
    stripe_invoice_id = models.CharField(max_length=100, unique=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(max_length=50)
    billing_reason = models.CharField(max_length=100, null=True, blank=True)
    invoice_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - ${self.amount_paid} - {self.status}"
