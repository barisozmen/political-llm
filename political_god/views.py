from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
import json
from django.utils import timezone

from .models import (
    UserValues, GeneratedLaw, LawCategory, LawGenerationRequest,
    LawSearch, StateConstitution
)
from .forms import (
    UserValuesForm, LawGenerationForm, LawSearchForm, LawEditForm,
    ConstitutionForm, AIConstitutionForm
)
from .services import PoliticalGodAI, get_user_law_stats
from billing.models import UserSubscription


def dashboard(request):
    """Main dashboard/homepage for Political God LLM"""
    # If user is not authenticated, show landing page
    if not request.user.is_authenticated:
        return render(request, 'political_god/homepage.html')
    
    # For authenticated users, show dashboard
    context = {}
    
    # Get user subscription info
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        context['subscription'] = subscription
        context['credits_remaining'] = subscription.credits_remaining
    except UserSubscription.DoesNotExist:
        context['subscription'] = None
        context['credits_remaining'] = 0
    
    # Get user values
    try:
        user_values = UserValues.objects.get(user=request.user)
        context['user_values'] = user_values
        context['values_configured'] = True
    except UserValues.DoesNotExist:
        context['values_configured'] = False
    
    # Get user stats
    context['stats'] = get_user_law_stats(request.user)
    
    # Get recent laws
    context['recent_laws'] = GeneratedLaw.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get recent requests
    context['recent_requests'] = LawGenerationRequest.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Check if user has constitution
    try:
        constitution = StateConstitution.objects.get(user=request.user)
        context['has_constitution'] = True
        context['constitution'] = constitution
    except StateConstitution.DoesNotExist:
        context['has_constitution'] = False
    
    return render(request, 'political_god/dashboard.html', context)


@login_required
def setup_values(request):
    """Setup or edit user's political values"""
    try:
        user_values = UserValues.objects.get(user=request.user)
    except UserValues.DoesNotExist:
        user_values = None
    
    if request.method == 'POST':
        form = UserValuesForm(request.POST, instance=user_values)
        if form.is_valid():
            values = form.save(commit=False)
            values.user = request.user
            values.save()
            messages.success(request, '🎉 Your political values have been saved! The AI will now generate laws aligned with your vision.')
            return redirect('political_god:dashboard')
    else:
        form = UserValuesForm(instance=user_values)
    
    return render(request, 'political_god/setup_values.html', {'form': form})


@login_required
def generate_law(request):
    """Generate a new law using AI"""
    if request.method == 'POST':
        form = LawGenerationForm(request.POST)
        if form.is_valid():
            ai_service = PoliticalGodAI()
            result = ai_service.generate_law(
                user=request.user,
                prompt=form.cleaned_data['prompt'],
                category=form.cleaned_data.get('category')
            )
            
            if result['success']:
                messages.success(request, f'🏛️ Law "{result["law"].title}" has been generated successfully!')
                return redirect('political_god:law_detail', law_id=result['law'].id)
            else:
                messages.error(request, f'❌ Error generating law: {result["error"]}')
    else:
        form = LawGenerationForm()
    
    # Get user's credit balance
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        credits_remaining = subscription.credits_remaining
    except UserSubscription.DoesNotExist:
        credits_remaining = 0
    
    return render(request, 'political_god/generate_law.html', {
        'form': form,
        'credits_remaining': credits_remaining
    })


@login_required
def law_library(request):
    """Browse and search user's generated laws"""
    laws = GeneratedLaw.objects.filter(user=request.user)
    search_form = LawSearchForm(request.GET)
    
    # Handle search
    if request.GET.get('search') and search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')
        is_favorite = search_form.cleaned_data.get('is_favorite')
        is_implemented = search_form.cleaned_data.get('is_implemented')
        
        # Use AI service for search (costs credits)
        ai_service = PoliticalGodAI()
        filters = {}
        if category:
            filters['category'] = category.name
        if is_favorite:
            filters['is_favorite'] = True
        if is_implemented:
            filters['is_implemented'] = True
            
        result = ai_service.search_laws(request.user, query or '', filters)
        
        if result['success']:
            laws = result['results']
            messages.info(request, f'🔍 Found {result["count"]} law(s) matching your search.')
        else:
            messages.error(request, f'❌ Search error: {result["error"]}')
    
    # Pagination
    paginator = Paginator(laws, 12)  # 12 laws per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = LawCategory.objects.all()
    
    return render(request, 'political_god/law_library.html', {
        'page_obj': page_obj,
        'search_form': search_form,
        'categories': categories
    })


@login_required
def law_detail(request, law_id):
    """View details of a specific law"""
    law = get_object_or_404(GeneratedLaw, id=law_id, user=request.user)
    return render(request, 'political_god/law_detail.html', {'law': law})


@login_required
def law_edit(request, law_id):
    """Edit a generated law"""
    law = get_object_or_404(GeneratedLaw, id=law_id, user=request.user)
    
    if request.method == 'POST':
        form = LawEditForm(request.POST, instance=law)
        if form.is_valid():
            form.save()
            messages.success(request, f'📝 Law "{law.title}" has been updated!')
            return redirect('political_god:law_detail', law_id=law.id)
    else:
        form = LawEditForm(instance=law)
    
    return render(request, 'political_god/law_edit.html', {
        'form': form,
        'law': law
    })


@login_required
def law_delete(request, law_id):
    """Delete a generated law"""
    law = get_object_or_404(GeneratedLaw, id=law_id, user=request.user)
    
    if request.method == 'POST':
        law_title = law.title
        law.delete()
        messages.success(request, f'🗑️ Law "{law_title}" has been deleted.')
        return redirect('political_god:law_library')
    
    return render(request, 'political_god/law_delete.html', {'law': law})


@login_required
def toggle_favorite(request, law_id):
    """Toggle favorite status of a law (AJAX)"""
    if request.method == 'POST':
        law = get_object_or_404(GeneratedLaw, id=law_id, user=request.user)
        law.is_favorite = not law.is_favorite
        law.save()
        
        return JsonResponse({
            'success': True,
            'is_favorite': law.is_favorite,
            'message': '⭐ Added to favorites!' if law.is_favorite else '☆ Removed from favorites!'
        })
    
    return JsonResponse({'success': False})


@login_required
def constitution(request):
    """View or create state constitution"""
    try:
        constitution = StateConstitution.objects.get(user=request.user)
    except StateConstitution.DoesNotExist:
        constitution = None
    
    if request.method == 'POST':
        if 'generate_ai' in request.POST:
            # Redirect to AI generation
            return redirect('political_god:constitution_ai')
        else:
            # Manual form submission
            form = ConstitutionForm(request.POST, instance=constitution)
            if form.is_valid():
                const = form.save(commit=False)
                const.user = request.user
                const.save()
                messages.success(request, '📜 Your state constitution has been saved!')
                return redirect('political_god:constitution')
    else:
        form = ConstitutionForm(instance=constitution)
    
    return render(request, 'political_god/constitution.html', {
        'form': form,
        'constitution': constitution
    })


@login_required
def constitution_ai(request):
    """AI-assisted constitution generation"""
    if request.method == 'POST':
        form = AIConstitutionForm(request.POST)
        if form.is_valid():
            ai_service = PoliticalGodAI()
            requirements = {
                'name': form.cleaned_data['name'],
                'population': form.cleaned_data.get('population', ''),
                'geography': form.cleaned_data.get('geography', ''),
                'focus_areas': form.cleaned_data.get('focus_areas', '')
            }
            
            result = ai_service.generate_constitution(request.user, requirements)
            
            if result['success']:
                messages.success(request, f'🏛️ Constitution for "{result["constitution"].name}" has been generated!')
                return redirect('political_god:constitution')
            else:
                messages.error(request, f'❌ Error generating constitution: {result["error"]}')
    else:
        form = AIConstitutionForm()
    
    # Get user's credit balance
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        credits_remaining = subscription.credits_remaining
    except UserSubscription.DoesNotExist:
        credits_remaining = 0
    
    return render(request, 'political_god/constitution_ai.html', {
        'form': form,
        'credits_remaining': credits_remaining
    })


@login_required
def analytics(request):
    """User analytics and usage statistics"""
    stats = get_user_law_stats(request.user)
    
    # Get subscription info
    try:
        subscription = UserSubscription.objects.get(user=request.user)
    except UserSubscription.DoesNotExist:
        subscription = None
    
    # Get recent activity
    recent_requests = LawGenerationRequest.objects.filter(user=request.user).order_by('-created_at')[:10]
    recent_searches = LawSearch.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Get law categories breakdown
    category_stats = {}
    for law in GeneratedLaw.objects.filter(user=request.user):
        if law.category:
            category_name = law.category.name
            category_stats[category_name] = category_stats.get(category_name, 0) + 1
    
    return render(request, 'political_god/analytics.html', {
        'stats': stats,
        'subscription': subscription,
        'recent_requests': recent_requests,
        'recent_searches': recent_searches,
        'category_stats': category_stats
    })


@login_required
def quick_generate(request):
    """Quick law generation for mobile users (simplified interface)"""
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '').strip()
        if prompt:
            ai_service = PoliticalGodAI()
            result = ai_service.generate_law(user=request.user, prompt=prompt)
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'law_id': str(result['law'].id),
                    'title': result['law'].title,
                    'summary': result['law'].summary,
                    'redirect_url': f'/political-god/law/{result["law"].id}/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def export_laws(request):
    """Export all laws as JSON"""
    laws = GeneratedLaw.objects.filter(user=request.user)
    
    export_data = {
        'user': request.user.username,
        'export_date': str(timezone.now()),
        'total_laws': laws.count(),
        'laws': []
    }
    
    for law in laws:
        export_data['laws'].append({
            'id': str(law.id),
            'title': law.title,
            'summary': law.summary,
            'content': law.content,
            'category': law.category.name if law.category else None,
            'tags': law.tag_list,
            'is_favorite': law.is_favorite,
            'is_implemented': law.is_implemented,
            'created_at': law.created_at.isoformat(),
            'updated_at': law.updated_at.isoformat()
        })
    
    response = JsonResponse(export_data, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="laws_export_{request.user.username}.json"'
    return response


# API Views for mobile app integration
@login_required
@require_http_methods(["GET"])
def api_stats(request):
    """API endpoint for user statistics"""
    stats = get_user_law_stats(request.user)
    
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        credits_remaining = subscription.credits_remaining
    except UserSubscription.DoesNotExist:
        credits_remaining = 0
    
    return JsonResponse({
        'stats': stats,
        'credits_remaining': credits_remaining
    })


@login_required
@require_http_methods(["GET"])
def api_recent_laws(request):
    """API endpoint for recent laws"""
    laws = GeneratedLaw.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    laws_data = []
    for law in laws:
        laws_data.append({
            'id': str(law.id),
            'title': law.title,
            'summary': law.summary,
            'category': law.category.name if law.category else None,
            'is_favorite': law.is_favorite,
            'is_implemented': law.is_implemented,
            'created_at': law.created_at.isoformat()
        })
    
    return JsonResponse({'laws': laws_data})
