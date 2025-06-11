from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, CreditUsage, BillingHistory


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'monthly_price', 'credits_per_month', 'is_active', 'created_at')
    list_filter = ('is_active', 'name')
    search_fields = ('display_name', 'name')
    ordering = ('monthly_price',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Plan Details', {
            'fields': ('name', 'display_name', 'stripe_price_id')
        }),
        ('Pricing & Credits', {
            'fields': ('monthly_price', 'credits_per_month')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_plan', 'status', 'credits_used', 'credits_remaining', 'current_period_end')
    list_filter = ('status', 'subscription_plan__name', 'created_at')
    search_fields = ('user__email', 'user__username', 'stripe_customer_id', 'stripe_subscription_id')
    ordering = ('-created_at',)
    readonly_fields = ('stripe_customer_id', 'stripe_subscription_id', 'created_at', 'updated_at', 'credits_remaining', 'usage_percentage', 'is_active')
    
    fieldsets = (
        ('User & Plan', {
            'fields': ('user', 'subscription_plan', 'status')
        }),
        ('Stripe Details', {
            'fields': ('stripe_customer_id', 'stripe_subscription_id'),
            'classes': ('collapse',)
        }),
        ('Billing Cycle', {
            'fields': ('current_period_start', 'current_period_end')
        }),
        ('Credit Usage', {
            'fields': ('credits_used', 'credits_remaining', 'usage_percentage', 'credits_reset_date')
        }),
        ('Status Info', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def credits_remaining(self, obj):
        return obj.credits_remaining
    credits_remaining.short_description = 'Credits Remaining'
    
    def usage_percentage(self, obj):
        return f"{obj.usage_percentage:.1f}%"
    usage_percentage.short_description = 'Usage %'
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'Active'


@admin.register(CreditUsage)
class CreditUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'timestamp', 'billing_period_start')
    list_filter = ('timestamp', 'billing_period_start')
    search_fields = ('user__email', 'user__username', 'description')
    ordering = ('-timestamp',)
    readonly_fields = ('id', 'timestamp')
    
    fieldsets = (
        ('Usage Details', {
            'fields': ('user', 'subscription', 'amount', 'description')
        }),
        ('Billing Period', {
            'fields': ('billing_period_start', 'billing_period_end')
        }),
        ('Metadata', {
            'fields': ('id', 'timestamp'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BillingHistory)
class BillingHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_paid', 'currency', 'status', 'billing_reason', 'created_at')
    list_filter = ('status', 'currency', 'billing_reason', 'created_at')
    search_fields = ('user__email', 'user__username', 'stripe_invoice_id')
    ordering = ('-created_at',)
    readonly_fields = ('stripe_invoice_id', 'created_at')
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('user', 'amount_paid', 'currency', 'status')
        }),
        ('Invoice Details', {
            'fields': ('stripe_invoice_id', 'billing_reason', 'invoice_url')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
