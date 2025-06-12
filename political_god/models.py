from django.db import models
from django.contrib.auth.models import User
import uuid


class UserValues(models.Model):
    """Stores user's core values and principles that guide law generation"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='values')
    
    # Core Values & Principles
    political_philosophy = models.TextField(
        max_length=2000,
        help_text="Your political philosophy and worldview",
        blank=True
    )
    core_values = models.TextField(
        max_length=2000,
        help_text="Your fundamental values (e.g., freedom, equality, justice, security)",
        blank=True
    )
    governance_style = models.CharField(
        max_length=100,
        choices=[
            ('democratic', 'Democratic'),
            ('technocratic', 'Technocratic'),
            ('libertarian', 'Libertarian'),
            ('progressive', 'Progressive'),
            ('conservative', 'Conservative'),
            ('socialist', 'Socialist'),
            ('anarchist', 'Anarchist'),
            ('mixed', 'Mixed Approach'),
            ('custom', 'Custom'),
        ],
        default='democratic'
    )
    priority_areas = models.TextField(
        max_length=1500,
        help_text="Key areas of focus for your state (e.g., technology, environment, economy)",
        blank=True
    )
    
    # Constitutional Framework
    individual_rights = models.TextField(
        max_length=1500,
        help_text="Individual rights and freedoms you want to protect",
        blank=True
    )
    collective_responsibilities = models.TextField(
        max_length=1500,
        help_text="Collective duties and social responsibilities",
        blank=True
    )
    
    # Economic Philosophy
    economic_system = models.CharField(
        max_length=100,
        choices=[
            ('free_market', 'Free Market Capitalism'),
            ('social_market', 'Social Market Economy'),
            ('mixed_economy', 'Mixed Economy'),
            ('planned_economy', 'Planned Economy'),
            ('ubi_economy', 'Universal Basic Income Economy'),
            ('post_scarcity', 'Post-Scarcity Economy'),
            ('custom', 'Custom Economic Model'),
        ],
        default='mixed_economy'
    )
    
    # Additional Context
    cultural_considerations = models.TextField(
        max_length=1500,
        help_text="Cultural values and considerations specific to your state",
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Values & Principles"
    
    @property
    def system_prompt(self):
        """Generate a comprehensive system prompt for the AI based on user values"""
        prompt_parts = [
            "You are the Political God LLM, an advanced AI system designed to generate laws for a futuristic network state.",
            "Generate laws that are:",
            "- Specific and actionable",
            "- Enforceable and practical",
            "- Consistent with the user's values",
            "- Forward-thinking and innovative",
            "- Respectful of individual rights while serving collective good",
            "",
            "USER'S VALUES AND PRINCIPLES:",
        ]
        
        if self.political_philosophy:
            prompt_parts.append(f"Political Philosophy: {self.political_philosophy}")
        
        if self.core_values:
            prompt_parts.append(f"Core Values: {self.core_values}")
        
        prompt_parts.append(f"Governance Style: {self.get_governance_style_display()}")
        
        if self.priority_areas:
            prompt_parts.append(f"Priority Areas: {self.priority_areas}")
        
        if self.individual_rights:
            prompt_parts.append(f"Individual Rights: {self.individual_rights}")
        
        if self.collective_responsibilities:
            prompt_parts.append(f"Collective Responsibilities: {self.collective_responsibilities}")
        
        prompt_parts.append(f"Economic System: {self.get_economic_system_display()}")
        
        if self.cultural_considerations:
            prompt_parts.append(f"Cultural Considerations: {self.cultural_considerations}")
        
        return "\n".join(prompt_parts)


class LawCategory(models.Model):
    """Categories for organizing laws"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    icon = models.CharField(max_length=50, default='fas fa-balance-scale')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Law Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class GeneratedLaw(models.Model):
    """Stores AI-generated laws"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_laws')
    
    # Law Content
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(max_length=500, blank=True)
    category = models.ForeignKey(LawCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Generation Context
    prompt_used = models.TextField(help_text="The prompt that generated this law")
    ai_model = models.CharField(max_length=50, default='gpt-4')
    system_prompt = models.TextField(help_text="The system prompt (user values) used")
    
    # Metadata
    is_favorite = models.BooleanField(default=False)
    is_implemented = models.BooleanField(default=False)
    implementation_notes = models.TextField(blank=True)
    
    # Tags for better organization
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def tag_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class LawGenerationRequest(models.Model):
    """Tracks law generation requests for analytics and billing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='law_requests')
    
    # Request Details
    prompt = models.TextField()
    category = models.ForeignKey(LawCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Generation Results
    generated_law = models.ForeignKey(GeneratedLaw, on_delete=models.CASCADE, null=True, blank=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    # Billing
    credits_used = models.IntegerField(default=10)
    billing_processed = models.BooleanField(default=False)
    
    # Performance Metrics
    response_time_seconds = models.FloatField(null=True, blank=True)
    token_count = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Law Request by {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class LawSearch(models.Model):
    """Tracks law searches for analytics and billing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='law_searches')
    
    # Search Details
    query = models.CharField(max_length=500)
    filters = models.JSONField(default=dict, blank=True)
    results_count = models.IntegerField(default=0)
    
    # Billing
    credits_used = models.IntegerField(default=1)
    billing_processed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Search: '{self.query}' by {self.user.username}"


class StateConstitution(models.Model):
    """User's constitutional framework for their network state"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='constitution')
    
    # Basic Framework
    name = models.CharField(max_length=200, help_text="Name of your network state")
    preamble = models.TextField(help_text="Constitutional preamble")
    
    # Fundamental Principles
    fundamental_rights = models.TextField(help_text="Bill of rights")
    governmental_structure = models.TextField(help_text="How the state is organized")
    amendment_process = models.TextField(help_text="How laws can be changed")
    
    # Generated Content
    is_ai_assisted = models.BooleanField(default=False)
    ai_generation_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Constitution of {self.name}"
