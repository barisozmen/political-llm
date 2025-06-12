from django.urls import path
from . import views

app_name = 'political_god'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard, name='dashboard'),
    
    # User values setup
    path('setup-values/', views.setup_values, name='setup_values'),
    
    # Law generation
    path('generate/', views.generate_law, name='generate_law'),
    path('quick-generate/', views.quick_generate, name='quick_generate'),
    
    # Law library and management
    path('library/', views.law_library, name='law_library'),
    path('law/<uuid:law_id>/', views.law_detail, name='law_detail'),
    path('law/<uuid:law_id>/edit/', views.law_edit, name='law_edit'),
    path('law/<uuid:law_id>/delete/', views.law_delete, name='law_delete'),
    path('law/<uuid:law_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # Constitution
    path('constitution/', views.constitution, name='constitution'),
    path('constitution/ai/', views.constitution_ai, name='constitution_ai'),
    
    # Analytics and export
    path('analytics/', views.analytics, name='analytics'),
    path('export/', views.export_laws, name='export_laws'),
    
    # API endpoints
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/recent-laws/', views.api_recent_laws, name='api_recent_laws'),
] 