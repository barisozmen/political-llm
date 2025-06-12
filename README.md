# Political God LLM - AI-Powered Network State Law Generation

An AI-first, mobile-first platform for generating laws and constitutional frameworks for network states. Built with Django 5.1.2, OpenAI GPT-4, Bootstrap 5, and integrated Stripe billing.

## 🏛️ Features

### 🤖 **AI-Powered Law Generation**
- Generate laws based on your political values and principles
- Powered by OpenAI GPT-4 for intelligent, context-aware legal content
- Credit-based usage system (10 credits per law generation)

### ⚖️ **Constitutional Framework**
- Create and manage your network state's constitution
- AI-assisted constitution generation (50 credits)
- Structured constitutional sections with proper legal formatting

### 🎯 **Values-Driven System**
- Configure your political philosophy and core values
- AI uses your values as system prompts for consistent law generation
- Support for various governance styles (democratic, technocratic, libertarian, etc.)

### 📚 **Law Library & Management**
- Organize laws by categories (Constitutional, Economic, Technology, etc.)
- Search and filter laws (1 credit per search)
- Mark laws as favorites or implemented
- Tag system for easy organization

### 💳 **Integrated Billing System**
- **Starter Plan**: $10/month - 1000 credits
- **Pro Plan**: $50/month - 5000 credits  
- **Premium Plan**: $100/month - 10000 credits
- Stripe integration for secure payments

### 🔐 **Authentication & User Management**
- Google OAuth2 integration
- Magic Link (passwordless) authentication
- Extended user profiles with political preferences
- Secure session management

### 📱 **Mobile-First Design**
- Responsive Bootstrap 5 interface
- Touch-optimized interactions
- Progressive Web App features
- Floating action buttons for quick access

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
- Add your `OPENAI_API_KEY` (required for law generation)
- Configure Stripe keys for billing
- Add Google OAuth credentials

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py setup_political_god  # Set up initial data
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to start building your network state!

## 🎮 Getting Started with Political God LLM

1. **Sign in** using Google OAuth or Magic Link
2. **Set up your values** at `/political-god/setup-values/`
3. **Configure your subscription** for credits
4. **Generate your first law** describing what you want to create
5. **Build your constitution** for your network state foundation
6. **Manage your laws** in the comprehensive library

## Core Components

### Law Generation Process

1. **User Input**: Describe the law you want to create
2. **AI Processing**: GPT-4 generates law based on your values
3. **Structured Output**: Law includes title, summary, content, and tags
4. **Credit Deduction**: 10 credits deducted from user account
5. **Storage**: Law saved to user's library for future reference

### Values System

The Political God LLM uses your configured values as system prompts:
- **Political Philosophy**: Your overall worldview
- **Core Values**: Fundamental principles (freedom, equality, etc.)
- **Governance Style**: Democratic, technocratic, libertarian, etc.
- **Economic System**: Free market, mixed economy, etc.
- **Priority Areas**: Technology, environment, social welfare, etc.

### Credit System

- **Law Generation**: 10 credits
- **Law Search**: 1 credit
- **Constitution Generation**: 50 credits
- Credits reset monthly based on subscription plan

## Project Structure

```
political-llm/
├── political_god/          # Main Political God LLM app
│   ├── models.py           # Law, values, and constitution models
│   ├── views.py            # Dashboard, generation, library views
│   ├── services.py         # OpenAI integration service
│   ├── forms.py            # Crispy forms for user input
│   └── admin.py            # Admin interface
├── authentication/         # User authentication system
├── billing/               # Stripe billing integration
├── templates/             # HTML templates
│   └── political_god/     # Political God LLM templates
├── static/               # Static assets
└── core/                 # Django settings and config
```

## API Endpoints

### Political God LLM URLs
- `/political-god/` - Main dashboard
- `/political-god/setup-values/` - Configure political values
- `/political-god/generate/` - Generate new law
- `/political-god/library/` - Law library and search
- `/political-god/constitution/` - Constitutional framework
- `/political-god/analytics/` - Usage analytics

### Authentication
- `/accounts/login/` - Login page with Google OAuth
- `/auth/magic-link/` - Request magic link
- `/auth/profile/` - User profile management

### Billing
- `/billing/dashboard/` - Subscription management
- `/billing/subscribe/` - Subscribe to plans

## Configuration Options

### OpenAI Settings
```python
OPENAI_API_KEY = 'your-openai-api-key'  # Required for law generation
```

### Stripe Settings (for billing)
```python
STRIPE_PUBLISHABLE_KEY = 'pk_...'
STRIPE_SECRET_KEY = 'sk_...'
STRIPE_WEBHOOK_SECRET = 'whsec_...'
```

### Political God LLM Settings
```python
# Credit costs (configurable)
LAW_GENERATION_COST = 10
SEARCH_COST = 1  
CONSTITUTION_COST = 50
```

## Models Overview

### Core Models

- **UserValues**: Stores user's political philosophy and values
- **GeneratedLaw**: AI-generated laws with metadata
- **LawCategory**: Categorization system (Constitutional, Economic, etc.)
- **StateConstitution**: Constitutional framework for network state
- **LawGenerationRequest**: Tracks generation requests and billing
- **LawSearch**: Tracks search usage for billing

### Features

- **UUID primary keys** for security
- **Timestamped models** for audit trails
- **Credit tracking** for billing integration
- **Tag system** for law organization
- **Favorite and implementation status** tracking

## Mobile Features

- **Responsive design** works on all screen sizes
- **Touch-optimized** buttons and interactions
- **Floating action button** for quick law generation
- **Swipe gestures** for navigation
- **Offline storage** for drafts and favorites

## Security Features

- **CSRF protection** on all forms
- **Secure API keys** stored in environment variables
- **User isolation** - users only see their own laws
- **Rate limiting** through credit system
- **Input validation** and sanitization

## AI Integration

### OpenAI GPT-4 Integration
- **System prompts** based on user values
- **Structured JSON output** for consistent formatting
- **Error handling** and fallback content
- **Token counting** for usage analytics
- **Temperature optimization** for legal content

### Content Quality
- **Values alignment** ensures consistency
- **Legal formatting** with articles and sections
- **Enforcement mechanisms** included in laws
- **Practical applicability** for network states

## Deployment

For production deployment:

1. Set `DEBUG=False` in environment
2. Configure production database (PostgreSQL recommended)
3. Set up Redis for caching and sessions
4. Configure HTTPS and SSL certificates
5. Set up monitoring and logging
6. Configure backup systems for user data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## License

This project is open source and available under the MIT License.

---

**🏛️ Build the future of governance with Political God LLM - where AI meets political innovation!**
