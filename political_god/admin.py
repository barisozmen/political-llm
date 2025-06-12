from django.contrib import admin
from .models import (
    UserValues, LawCategory, GeneratedLaw, LawGenerationRequest, 
    LawSearch, StateConstitution
)


@admin.register(UserValues)
class UserValuesAdmin(admin.ModelAdmin):
    list_display = ('user', 'governance_style', 'economic_system', 'created_at')
    list_filter = ('governance_style', 'economic_system', 'created_at')
    search_fields = ('user__username', 'user__email', 'political_philosophy', 'core_values')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Political Framework', {
            'fields': ('political_philosophy', 'core_values', 'governance_style'),
            'classes': ('wide',)
        }),
        ('Priorities & Rights', {
            'fields': ('priority_areas', 'individual_rights', 'collective_responsibilities'),
            'classes': ('wide',)
        }),
        ('Economic System', {
            'fields': ('economic_system',)
        }),
        ('Cultural Context', {
            'fields': ('cultural_considerations',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LawCategory)
class LawCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'icon', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('icon',)
    ordering = ('name',)


@admin.register(GeneratedLaw)
class GeneratedLawAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'is_favorite', 'is_implemented', 'created_at')
    list_filter = ('category', 'is_favorite', 'is_implemented', 'ai_model', 'created_at')
    search_fields = ('title', 'content', 'summary', 'tags', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_editable = ('is_favorite', 'is_implemented')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'category')
        }),
        ('Law Content', {
            'fields': ('summary', 'content'),
            'classes': ('wide',)
        }),
        ('Generation Context', {
            'fields': ('prompt_used', 'ai_model', 'system_prompt'),
            'classes': ('collapse', 'wide')
        }),
        ('Metadata', {
            'fields': ('is_favorite', 'is_implemented', 'implementation_notes', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LawGenerationRequest)
class LawGenerationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'success', 'credits_used', 'response_time_seconds', 'created_at')
    list_filter = ('success', 'billing_processed', 'category', 'created_at')
    search_fields = ('user__username', 'prompt', 'error_message')
    readonly_fields = ('id', 'created_at')
    
    fieldsets = (
        ('Request Details', {
            'fields': ('id', 'user', 'prompt', 'category')
        }),
        ('Results', {
            'fields': ('generated_law', 'success', 'error_message')
        }),
        ('Billing & Performance', {
            'fields': ('credits_used', 'billing_processed', 'response_time_seconds', 'token_count')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


@admin.register(LawSearch)
class LawSearchAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'results_count', 'credits_used', 'created_at')
    list_filter = ('billing_processed', 'created_at')
    search_fields = ('user__username', 'query')
    readonly_fields = ('id', 'created_at')


@admin.register(StateConstitution)
class StateConstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_ai_assisted', 'created_at')
    list_filter = ('is_ai_assisted', 'created_at')
    search_fields = ('name', 'user__username', 'preamble')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name')
        }),
        ('Constitutional Framework', {
            'fields': ('preamble', 'fundamental_rights', 'governmental_structure', 'amendment_process'),
            'classes': ('wide',)
        }),
        ('AI Assistance', {
            'fields': ('is_ai_assisted', 'ai_generation_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
