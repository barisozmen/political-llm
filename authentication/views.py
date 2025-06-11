from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from sesame.utils import get_token
from .models import UserProfile
from .forms import MagicLinkForm, UserProfileForm
import logging
import urllib.parse
import requests
import json
import logfire

logger = logging.getLogger(__name__)


def custom_logout_view(request):
    """Custom logout view that logs out the user and redirects to home"""
    user_email = request.user.email if request.user.is_authenticated else "anonymous"
    
    logfire.info("User logout initiated", user_email=user_email)
    
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    
    logfire.info("User logout completed", user_email=user_email)
    
    return redirect('app:home')


class CustomLoginView(TemplateView):
    template_name = 'account/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MagicLinkForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = MagicLinkForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            logfire.info("Magic link request initiated", email=email, request_type="post")
            
            try:
                # User exists - send sign-in link
                user = User.objects.get(email=email)
                token = get_token(user)
                magic_link = request.build_absolute_uri(
                    reverse('authentication:magic_link_login') + f'?sesame={token}'
                )
                
                logfire.info("Magic link generated for existing user", 
                           user_id=user.id, 
                           email=email,
                           link_type="signin")
                
                send_mail(
                    subject='Sign in to Django Auth Template',
                    message=f'''
Hello {user.username},

Click the link below to sign in to your account:

{magic_link}

This link will expire in 1 hour and can only be used once.

If you didn't request this, please ignore this email.

Best regards,
Django Auth Template Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                logfire.info("Magic link email sent successfully", 
                           email=email, 
                           link_type="signin")
                
                messages.success(
                    request,
                    f'Welcome back! A sign-in link has been sent to {email}. Please check your email and click the link to access your account.'
                )
                
            except User.DoesNotExist:
                # User doesn't exist - send sign-up link
                signup_token = self.generate_signup_token(email)
                magic_link = request.build_absolute_uri(
                    reverse('authentication:magic_link_signup') + f'?token={signup_token}&email={email}'
                )
                
                logfire.info("Magic link generated for new user", 
                           email=email,
                           link_type="signup")
                
                send_mail(
                    subject='Welcome to Django Auth Template - Complete Your Registration',
                    message=f'''
Hello!

Welcome to Django Auth Template! We noticed this is your first time signing in.

Click the link below to create your account and sign in:

{magic_link}

This link will expire in 1 hour and can only be used once.

If you didn't request this, please ignore this email.

Best regards,
Django Auth Template Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                logfire.info("Magic link email sent successfully", 
                           email=email, 
                           link_type="signup")
                
                messages.success(
                    request,
                    f'Welcome! Since this is your first time, we\'ve sent a registration link to {email}. Please check your email and click the link to create your account and sign in.'
                )
            
            except Exception as e:
                logfire.error("Magic link generation failed", 
                            email=email, 
                            error=str(e),
                            exc_info=True)
                messages.error(request, 'There was an error sending your magic link. Please try again.')
                
            return redirect('account_login')
        
        logfire.warning("Magic link form validation failed", 
                       form_errors=form.errors)
        
        return render(request, self.template_name, {'form': form})
    
    def generate_signup_token(self, email):
        """Generate a secure token for signup links"""
        import hashlib
        import time
        from django.conf import settings
        
        # Create a time-based token using minute precision (not seconds)
        # This ensures validation will work correctly
        current_minute = int(time.time() // 60)  # Get current minute timestamp
        secret_key = getattr(settings, 'SECRET_KEY', 'default-secret')
        token_string = f"{email}:{current_minute}:{secret_key}"
        return hashlib.sha256(token_string.encode()).hexdigest()[:32]


class MagicLinkSignupView(TemplateView):
    """Handle magic link signup for new users"""
    template_name = 'authentication/signup_success.html'
    
    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        email = request.GET.get('email')
        
        logfire.info("Magic link signup attempt", 
                    email=email,
                    has_token=bool(token),
                    request_ip=request.META.get('REMOTE_ADDR', ''))
        
        if not token or not email:
            logfire.warning("Invalid magic link signup - missing token or email", 
                          has_token=bool(token),
                          has_email=bool(email))
            messages.error(request, 'Invalid signup link. Please try again.')
            return redirect('account_login')
        
        # Validate token (simple validation - enhance for production)
        if not self.validate_signup_token(token, email):
            logfire.warning("Magic link signup token validation failed", 
                          email=email,
                          token_prefix=token[:8] + "..." if token else None)
            messages.error(request, 'This signup link has expired or is invalid. Please request a new one.')
            return redirect('account_login')
        
        try:
            # Check if user was created in the meantime
            user = User.objects.get(email=email)
            
            logfire.info("Magic link signup - user already exists", 
                        user_id=user.id,
                        email=email)
            
            messages.info(request, 'Account already exists! Logging you in...')
            
            # Ensure user has a profile (the signal should have created it, but just in case)
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user)
                logfire.info("Created missing UserProfile for existing user during magic link signup", 
                           user_id=user.id,
                           email=email)
                
        except User.DoesNotExist:
            # Create new user
            username = email.split('@')[0]  # Use email prefix as username
            counter = 1
            original_username = username
            
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email
            )
            
            logfire.info("New user created via magic link signup", 
                        user_id=user.id,
                        email=email,
                        username=username)
            
            # The UserProfile is automatically created by Django signals
            
            messages.success(request, f'Welcome! Your account has been created successfully. You are now signed in.')
        
        # Log the user in
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        logfire.info("Magic link signup login successful", 
                    user_id=user.id,
                    email=email)
        
        return redirect('authentication:profile')
    
    def validate_signup_token(self, token, email):
        """Validate signup token (simple implementation)"""
        import hashlib
        import time
        from django.conf import settings
        
        try:
            # Token should be valid for 1 hour (60 minutes)
            current_minute = int(time.time() // 60)
            secret_key = getattr(settings, 'SECRET_KEY', 'default-secret')
            
            # Check tokens generated in the last 60 minutes
            for minutes_ago in range(60):  # Check last 60 minutes
                test_minute = current_minute - minutes_ago
                test_token_string = f"{email}:{test_minute}:{secret_key}"
                test_token = hashlib.sha256(test_token_string.encode()).hexdigest()[:32]
                if test_token == token:
                    return True
            return False
        except Exception as e:
            # Log the error for debugging
            logger.error(f"Token validation error: {e}")
            return False


class MagicLinkView(TemplateView):
    template_name = 'authentication/magic_link.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MagicLinkForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = MagicLinkForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
                return render(request, self.template_name, {'form': form})
            
            # Generate magic link token
            token = get_token(user)
            magic_link = request.build_absolute_uri(
                reverse('authentication:magic_link_login') + f'?sesame={token}'
            )
            
            # Send email with magic link
            send_mail(
                subject='Your Magic Link for Django Auth Template',
                message=f'''
Hello {user.username},

You requested a magic link to sign in to your account. Click the link below:

{magic_link}

This link will expire in 1 hour and can only be used once.

If you didn't request this, please ignore this email.

Best regards,
Django Auth Template Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            messages.success(
                request,
                f'Magic link sent to {email}! Check your email and click the link to sign in.'
            )
            
        return render(request, self.template_name, {'form': form})


class MagicLinkSentView(TemplateView):
    """View to show magic link sent confirmation"""
    template_name = 'authentication/magic_link_sent.html'

class GoogleOAuthRedirectView(TemplateView):
    """Custom Google OAuth 2.0 redirect view"""
    
    def get(self, request, *args, **kwargs):
        logfire.info("Google OAuth redirect initiated", 
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    ip_address=request.META.get('REMOTE_ADDR', ''))
        
        if not settings.GOOGLE_OAUTH2_CLIENT_ID:
            logfire.error("Google OAuth not configured - missing client ID")
            messages.error(request, 'Google OAuth is not properly configured.')
            return redirect('/')
        
        # Build the redirect URI
        host = request.get_host()
        if host in ['127.0.0.1', 'localhost']:
            redirect_uri = request.build_absolute_uri('/auth/google-callback')
        elif host in settings.ALLOWED_HOSTS:
            redirect_uri = f'https://{host}/auth/google-callback'
        else:
            redirect_uri = f'https://{host}/auth/google-callback'
        
        logfire.info("Google OAuth redirect URI generated", 
                    host=host,
                    redirect_uri=redirect_uri)
        
        # Google OAuth2 authorization URL
        auth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        
        # OAuth2 parameters
        params = {
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'access_type': 'online',
            'include_granted_scopes': 'true',
            'state': request.session.session_key or 'default_state',
        }
        
        # Build the final URL
        google_oauth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
        
        logfire.info("Redirecting to Google OAuth", 
                    oauth_url=google_oauth_url[:100] + "..." if len(google_oauth_url) > 100 else google_oauth_url)
        
        return HttpResponseRedirect(google_oauth_url)


class GoogleOAuthCallbackView(TemplateView):
    """Custom Google OAuth 2.0 callback view"""
    
    def get(self, request, *args, **kwargs):
        # Get authorization code from callback
        code = request.GET.get('code')
        error = request.GET.get('error')
        state = request.GET.get('state')
        
        logfire.info("Google OAuth callback received", 
                    has_code=bool(code),
                    has_error=bool(error),
                    state=state,
                    callback_params=dict(request.GET))
        
        if error:
            logfire.error("Google OAuth callback error", 
                         oauth_error=error,
                         error_description=request.GET.get('error_description'))
            messages.error(request, f'Google OAuth error: {error}')
            return redirect('account_login')
        
        if not code:
            logfire.error("Google OAuth callback missing authorization code")
            messages.error(request, 'No authorization code received from Google.')
            return redirect('account_login')
        
        try:
            # Exchange authorization code for access token
            user_info = self.get_google_user_info(request, code)
            
            if not user_info:
                logfire.error("Failed to get user info from Google")
                messages.error(request, 'Failed to get user information from Google.')
                return redirect('account_login')
            
            logfire.info("Google user info retrieved", 
                        user_email=user_info.get('email'),
                        user_name=user_info.get('name'),
                        google_id=user_info.get('id'))
            
            # Create or get user
            user = self.get_or_create_user(user_info)
            
            if user:
                # Log the user in
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                logfire.info("Google OAuth login successful", 
                           user_id=user.id,
                           user_email=user.email,
                           is_new_user=user.date_joined.date() == user.last_login.date() if user.last_login else True)
                
                messages.success(request, f'Welcome, {user.first_name or user.username}!')
                return redirect('app:home')
            else:
                logfire.error("Failed to create or retrieve user from Google OAuth")
                messages.error(request, 'Failed to create or retrieve user account.')
                return redirect('account_login')
                
        except Exception as e:
            logfire.error("Google OAuth callback error", 
                         error=str(e),
                         exc_info=True)
            messages.error(request, 'An error occurred during Google sign-in. Please try again.')
            return redirect('account_login')
    
    def get_google_user_info(self, request, code):
        """Exchange authorization code for access token and get user info"""
        # Build redirect URI (must match the one used in authorization)
        host = request.get_host()
        if host in ['127.0.0.1', 'localhost']:
            redirect_uri = request.build_absolute_uri('/auth/google-callback')
        elif host in settings.ALLOWED_HOSTS:
            redirect_uri = f'https://{host}/auth/google-callback'
        else:
            redirect_uri = f'https://{host}/auth/google-callback'
        
        # Exchange code for access token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        }
        
        token_response = requests.post(token_url, data=token_data)
        
        if token_response.status_code != 200:
            logger.error(f"Token exchange failed: {token_response.text}")
            return None
        
        token_info = token_response.json()
        access_token = token_info.get('access_token')
        
        if not access_token:
            logger.error("No access token received")
            return None
        
        # Get user info from Google
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        user_response = requests.get(user_info_url, headers=headers)
        
        if user_response.status_code != 200:
            logger.error(f"User info request failed: {user_response.text}")
            return None
        
        return user_response.json()
    
    def get_or_create_user(self, user_info):
        """Create or get existing user from Google user info"""
        email = user_info.get('email')
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        google_id = user_info.get('id')
        
        if not email:
            logfire.error("No email in Google user info", user_info=user_info)
            return None
        
        try:
            # Try to get existing user by email
            user = User.objects.get(email=email)
            
            logfire.info("Existing user found for Google OAuth", 
                        user_id=user.id,
                        email=email,
                        existing_first_name=user.first_name,
                        google_first_name=first_name)
            
            # Update user info if needed
            updated_fields = []
            if not user.first_name and first_name:
                user.first_name = first_name
                updated_fields.append('first_name')
            if not user.last_name and last_name:
                user.last_name = last_name
                updated_fields.append('last_name')
            
            if updated_fields:
                user.save()
                logfire.info("Updated existing user info", 
                           user_id=user.id,
                           updated_fields=updated_fields)
            
            # Ensure user has a profile
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user)
                logfire.info("Created missing UserProfile for existing user", 
                           user_id=user.id,
                           email=email)
            
            return user
            
        except User.DoesNotExist:
            # Create new user
            username = email.split('@')[0]
            counter = 1
            original_username = username
            
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # The UserProfile is automatically created by Django signals
            
            logfire.info("Created new user from Google OAuth", 
                        user_id=user.id,
                        email=email,
                        username=username,
                        first_name=first_name,
                        last_name=last_name)
            
            return user


class ProfileView(LoginRequiredMixin, FormView):
    """User profile view with edit functionality"""
    template_name = 'authentication/profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('authentication:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user.profile
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.request.user.profile
        return context


@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('authentication:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'authentication/profile.html', {
        'form': form,
        'profile': profile
    })
