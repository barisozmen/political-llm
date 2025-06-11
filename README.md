# Django Authentication System

A complete Django authentication system featuring Google OAuth, Magic Link login, and comprehensive user management. Built with Django 5.1.2, Bootstrap 5, and SQLite.

## Features

- 🔐 **Passwordless Authentication Methods**:
  - Google OAuth2 integration
  - Magic Link (passwordless) authentication
  
- 👤 **User Management**:
  - Extended user profiles with avatars
  - Profile editing capabilities
  - Automatic email validation (no verification needed)
  - Social media integration (Twitter, Discord)
  - Cryptocurrency wallet addresses (ETH, Bitcoin)
  
- 🎨 **Modern UI**:
  - Responsive Bootstrap 5 design
  - Beautiful gradient backgrounds
  - Mobile-friendly interface
  
- 📧 **Email System**:
  - Console backend for development
  - SMTP support for production
  - Magic link email generation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` with your settings:
- Set your `SECRET_KEY`
- Configure email settings (optional for development)
- Add Google OAuth credentials (see Google Setup section)

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see the application.

## Google OAuth Setup

To enable Google Sign-In:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://127.0.0.1:8000/accounts/google/login/callback/`
5. Copy Client ID and Client Secret to your `.env` file
6. Run `python manage.py migrate` to create social application
7. In Django admin (`/admin/`), go to Social Applications
8. Add a new Social Application:
   - Provider: Google
   - Name: Google
   - Client ID: Your Google Client ID
   - Secret key: Your Google Client Secret
   - Sites: Add your site (default: example.com)

## Magic Link Setup

Magic links work out of the box with the console email backend. For production:

1. Configure SMTP settings in `.env`
2. Set `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
3. Users can request magic links at `/auth/magic-link/`

## Project Structure

```
django-auth-system/
├── authentication/          # Authentication app
│   ├── models.py           # UserProfile model
│   ├── views.py            # Auth views (magic link, profile)
│   ├── forms.py            # Custom forms
│   ├── admin.py            # Admin interface
│   └── urls.py             # Auth URLs
├── app/                    # Main app
│   ├── views.py            # Home view
│   └── urls.py             # Main URLs
├── core/                   # Django project settings
│   ├── settings.py         # Main settings
│   └── urls.py             # URL configuration
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── app/                # App templates
│   ├── authentication/     # Auth templates
│   └── account/            # Allauth templates
├── static/                 # Static files (created automatically)
├── media/                  # User uploads (created automatically)
└── requirements.txt        # Python dependencies
```

## Available URLs

- `/` - Home page
- `/accounts/login/` - Login page
- `/accounts/signup/` - Sign up page
- `/accounts/logout/` - Logout
- `/accounts/google/login/` - Google OAuth
- `/auth/magic-link/` - Request magic link
- `/auth/profile/` - User profile page
- `/admin/` - Django admin

## Models

### UserProfile
Extends Django's built-in User model with additional fields:
- `avatar` - Profile picture
- `bio` - User biography
- `website` - Personal website
- `twitter_handle` - Twitter username (without @)
- `discord_handle` - Discord username
- `eth_address` - Ethereum wallet address
- `bitcoin_address` - Bitcoin wallet address

## Configuration Options

### Email Settings
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'     # Production
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Magic Link Settings
```python
SESAME_MAX_AGE = 3600      # Link expires in 1 hour
SESAME_ONE_TIME = True     # Links can only be used once
```

### Allauth Settings
```python
ACCOUNT_AUTHENTICATION_METHOD = 'email'    # Use email instead of username
ACCOUNT_EMAIL_REQUIRED = True              # Email is required
ACCOUNT_EMAIL_VERIFICATION = 'none'        # No email verification needed (passwordless)
ACCOUNT_USERNAME_REQUIRED = False          # Don't require username
```

## Security Features

- CSRF protection enabled
- Secure passwordless authentication
- One-time magic links with expiration
- Time-limited secure tokens (1-hour expiry)
- Google OAuth security
- XSS protection headers
- Session security
- Ethereum address validation

## Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Configure proper `ALLOWED_HOSTS`
3. Set up SMTP email backend
4. Configure static file serving
5. Use environment variables for secrets
6. Set up HTTPS
7. Configure Google OAuth redirect URIs for production domain

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## License

This project is open source and available under the MIT License.
