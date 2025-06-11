from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'twitter_handle', 'discord_handle', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'twitter_handle', 'discord_handle', 'eth_address', 'bitcoin_address']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'avatar', 'bio', 'website')
        }),
        ('Social Media', {
            'fields': ('twitter_handle', 'discord_handle')
        }),
        ('Crypto Addresses', {
            'fields': ('eth_address', 'bitcoin_address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
