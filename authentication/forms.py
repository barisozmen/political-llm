from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class MagicLinkForm(forms.Form):
    """Form for requesting magic link"""
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'required': True,
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
        return email


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )

    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'website', 'twitter_handle', 'discord_handle', 'eth_address', 'bitcoin_address']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
            'twitter_handle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'username (without @)',
                'maxlength': 50
            }),
            'discord_handle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'YourDiscordName#1234',
                'maxlength': 50
            }),
            'eth_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0x...',
                'maxlength': 42
            }),
            'bitcoin_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'bc1... or 1... or 3...',
                'maxlength': 62
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['email'].initial = self.user.email

    def clean_twitter_handle(self):
        """Remove @ symbol if user includes it"""
        twitter_handle = self.cleaned_data.get('twitter_handle', '')
        if twitter_handle.startswith('@'):
            twitter_handle = twitter_handle[1:]
        return twitter_handle

    def clean_eth_address(self):
        """Basic validation for Ethereum address"""
        eth_address = self.cleaned_data.get('eth_address', '')
        if eth_address and not eth_address.startswith('0x'):
            raise forms.ValidationError('Ethereum address must start with 0x')
        if eth_address and len(eth_address) != 42:
            raise forms.ValidationError('Ethereum address must be 42 characters long')
        return eth_address

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        if self.user:
            # Update User fields
            self.user.email = self.cleaned_data['email']
            
            if commit:
                self.user.save()
                profile.save()
        
        return profile 