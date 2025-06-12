import openai
import time
import json
from django.conf import settings
from django.contrib.auth.models import User
from .models import (
    UserValues, GeneratedLaw, LawGenerationRequest, LawSearch, 
    LawCategory, StateConstitution
)
from billing.models import UserSubscription


class PoliticalGodAI:
    """AI service for generating laws and constitutional content"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4o"  # Using the latest GPT-4 model
        
    def generate_law(self, user: User, prompt: str, category: LawCategory = None) -> dict:
        """Generate a law based on user prompt and values"""
        start_time = time.time()
        
        try:
            # Check if user has credits
            if not self._check_credits(user, 10):
                return {
                    'success': False,
                    'error': 'Insufficient credits. Please upgrade your subscription.',
                    'credits_required': 10
                }
            
            # Get user values for system prompt
            user_values, created = UserValues.objects.get_or_create(user=user)
            system_prompt = user_values.system_prompt
            
            # Enhance the prompt with specific instructions
            enhanced_prompt = f"""
            {prompt}

            Please provide your response in the following JSON format:
            {{
                "title": "Short, descriptive title for the law",
                "summary": "Brief 2-3 sentence summary of the law's purpose and scope",
                "content": "Full detailed law text with specific articles, sections, and enforcement mechanisms",
                "tags": ["tag1", "tag2", "tag3"],
                "category_suggestion": "suggested category name"
            }}
            
            Make sure the law is:
            1. Specific and actionable with clear enforcement mechanisms
            2. Consistent with the user's stated values and principles
            3. Practical for a modern network state
            4. Forward-thinking and innovative
            5. Balanced between individual rights and collective good
            """
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            response_time = time.time() - start_time
            
            # Parse the response
            ai_response = response.choices[0].message.content
            
            try:
                # Try to parse as JSON
                law_data = json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback: extract content manually
                law_data = {
                    "title": "Generated Law",
                    "summary": "AI-generated law based on user prompt",
                    "content": ai_response,
                    "tags": [],
                    "category_suggestion": ""
                }
            
            # Create the law record
            generated_law = GeneratedLaw.objects.create(
                user=user,
                title=law_data.get('title', 'Generated Law'),
                content=law_data.get('content', ai_response),
                summary=law_data.get('summary', ''),
                category=category,
                prompt_used=prompt,
                ai_model=self.model,
                system_prompt=system_prompt,
                tags=', '.join(law_data.get('tags', []))
            )
            
            # Create request tracking record
            request_record = LawGenerationRequest.objects.create(
                user=user,
                prompt=prompt,
                category=category,
                generated_law=generated_law,
                success=True,
                credits_used=10,
                response_time_seconds=response_time,
                token_count=response.usage.total_tokens if hasattr(response, 'usage') else None
            )
            
            # Deduct credits
            self._use_credits(user, 10, f"Law generation: {generated_law.title}")
            
            return {
                'success': True,
                'law': generated_law,
                'request_id': request_record.id,
                'response_time': response_time,
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            # Log the error and create failed request record
            response_time = time.time() - start_time
            
            request_record = LawGenerationRequest.objects.create(
                user=user,
                prompt=prompt,
                category=category,
                success=False,
                error_message=str(e),
                response_time_seconds=response_time
            )
            
            return {
                'success': False,
                'error': str(e),
                'request_id': request_record.id
            }
    
    def search_laws(self, user: User, query: str, filters: dict = None) -> dict:
        """Search through user's generated laws"""
        
        try:
            # Check if user has credits
            if not self._check_credits(user, 1):
                return {
                    'success': False,
                    'error': 'Insufficient credits. Please upgrade your subscription.',
                    'credits_required': 1
                }
            
            # Build the search query
            laws = GeneratedLaw.objects.filter(user=user)
            
            # Apply text search
            if query:
                laws = laws.filter(
                    models.Q(title__icontains=query) |
                    models.Q(content__icontains=query) |
                    models.Q(summary__icontains=query) |
                    models.Q(tags__icontains=query)
                )
            
            # Apply filters
            if filters:
                if filters.get('category'):
                    laws = laws.filter(category__name=filters['category'])
                if filters.get('is_favorite'):
                    laws = laws.filter(is_favorite=True)
                if filters.get('is_implemented'):
                    laws = laws.filter(is_implemented=True)
                if filters.get('tags'):
                    for tag in filters['tags']:
                        laws = laws.filter(tags__icontains=tag)
            
            results = laws.order_by('-created_at')
            
            # Create search tracking record
            search_record = LawSearch.objects.create(
                user=user,
                query=query,
                filters=filters or {},
                results_count=results.count()
            )
            
            # Deduct credits
            self._use_credits(user, 1, f"Law search: '{query}'")
            
            return {
                'success': True,
                'results': results,
                'count': results.count(),
                'search_id': search_record.id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_constitution(self, user: User, requirements: dict) -> dict:
        """Generate a constitutional framework for the user's network state"""
        
        try:
            # Check if user has credits (constitution generation costs 50 credits)
            if not self._check_credits(user, 50):
                return {
                    'success': False,
                    'error': 'Insufficient credits. Constitution generation requires 50 credits.',
                    'credits_required': 50
                }
            
            # Get user values
            user_values, created = UserValues.objects.get_or_create(user=user)
            system_prompt = user_values.system_prompt
            
            # Create constitution generation prompt
            prompt = f"""
            Create a comprehensive constitutional framework for a network state based on the following requirements:
            
            State Name: {requirements.get('name', 'The Network State')}
            Population Size: {requirements.get('population', 'Not specified')}
            Geographic Scope: {requirements.get('geography', 'Digital-first with physical nodes')}
            Special Focus Areas: {requirements.get('focus_areas', 'Not specified')}
            
            Please provide a complete constitutional document with:
            1. Preamble stating the founding principles
            2. Bill of Rights protecting individual freedoms
            3. Governmental structure and organization
            4. Amendment process for future changes
            5. Enforcement mechanisms
            
            Format as a proper constitutional document with articles and sections.
            """
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=3000
            )
            
            constitution_text = response.choices[0].message.content
            
            # Parse the constitution into sections
            constitution_data = self._parse_constitution(constitution_text)
            
            # Create or update constitution record
            constitution, created = StateConstitution.objects.get_or_create(
                user=user,
                defaults={
                    'name': requirements.get('name', 'The Network State'),
                    'preamble': constitution_data.get('preamble', ''),
                    'fundamental_rights': constitution_data.get('rights', ''),
                    'governmental_structure': constitution_data.get('structure', ''),
                    'amendment_process': constitution_data.get('amendments', ''),
                    'is_ai_assisted': True,
                    'ai_generation_notes': f"Generated with {self.model} based on user values and requirements"
                }
            )
            
            if not created:
                # Update existing constitution
                constitution.name = requirements.get('name', constitution.name)
                constitution.preamble = constitution_data.get('preamble', constitution.preamble)
                constitution.fundamental_rights = constitution_data.get('rights', constitution.fundamental_rights)
                constitution.governmental_structure = constitution_data.get('structure', constitution.governmental_structure)
                constitution.amendment_process = constitution_data.get('amendments', constitution.amendment_process)
                constitution.is_ai_assisted = True
                constitution.ai_generation_notes = f"Updated with {self.model} on {time.strftime('%Y-%m-%d')}"
                constitution.save()
            
            # Deduct credits
            self._use_credits(user, 50, f"Constitution generation: {constitution.name}")
            
            return {
                'success': True,
                'constitution': constitution,
                'raw_text': constitution_text
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_credits(self, user: User, required_credits: int) -> bool:
        """Check if user has sufficient credits"""
        try:
            subscription = UserSubscription.objects.get(user=user)
            return subscription.credits_remaining >= required_credits
        except UserSubscription.DoesNotExist:
            return False
    
    def _use_credits(self, user: User, credits: int, description: str) -> bool:
        """Deduct credits from user's account"""
        try:
            subscription = UserSubscription.objects.get(user=user)
            return subscription.use_credits(credits, description)
        except UserSubscription.DoesNotExist:
            return False
    
    def _parse_constitution(self, text: str) -> dict:
        """Parse constitution text into structured sections"""
        sections = {}
        
        # Simple parsing - could be enhanced with more sophisticated NLP
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            if any(keyword in line.lower() for keyword in ['preamble', 'article i', 'bill of rights']):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                if 'preamble' in line.lower():
                    current_section = 'preamble'
                elif any(keyword in line.lower() for keyword in ['bill of rights', 'rights', 'article i']):
                    current_section = 'rights'
                elif any(keyword in line.lower() for keyword in ['government', 'structure', 'article ii']):
                    current_section = 'structure'
                elif any(keyword in line.lower() for keyword in ['amendment', 'change', 'modification']):
                    current_section = 'amendments'
                
                current_content = [line]
            else:
                current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections


# Utility functions
from django.db import models

def get_law_categories():
    """Get all available law categories"""
    return LawCategory.objects.all()

def get_user_law_stats(user: User) -> dict:
    """Get statistics about user's law generation"""
    stats = {
        'total_laws': GeneratedLaw.objects.filter(user=user).count(),
        'favorite_laws': GeneratedLaw.objects.filter(user=user, is_favorite=True).count(),
        'implemented_laws': GeneratedLaw.objects.filter(user=user, is_implemented=True).count(),
        'total_requests': LawGenerationRequest.objects.filter(user=user).count(),
        'successful_requests': LawGenerationRequest.objects.filter(user=user, success=True).count(),
        'total_searches': LawSearch.objects.filter(user=user).count(),
    }
    
    # Calculate success rate
    if stats['total_requests'] > 0:
        stats['success_rate'] = (stats['successful_requests'] / stats['total_requests']) * 100
    else:
        stats['success_rate'] = 0
    
    return stats 