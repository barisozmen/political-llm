from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML, Div
from crispy_forms.bootstrap import FormActions
from .models import UserValues, GeneratedLaw, StateConstitution, LawCategory


class UserValuesForm(forms.ModelForm):
    """Form for setting up user's political values and principles"""
    
    class Meta:
        model = UserValues
        fields = [
            'political_philosophy', 'core_values', 'governance_style', 
            'priority_areas', 'individual_rights', 'collective_responsibilities',
            'economic_system', 'cultural_considerations'
        ]
        
        widgets = {
            'political_philosophy': forms.Textarea(attrs={
                'placeholder': 'Describe your political philosophy, worldview, and fundamental beliefs about governance...',
                'rows': 4
            }),
            'core_values': forms.Textarea(attrs={
                'placeholder': 'List your core values (e.g., freedom, equality, justice, innovation, security, privacy, sustainability)...',
                'rows': 4
            }),
            'priority_areas': forms.Textarea(attrs={
                'placeholder': 'What areas should your state prioritize? (e.g., technology, environment, education, healthcare, economy)...',
                'rows': 3
            }),
            'individual_rights': forms.Textarea(attrs={
                'placeholder': 'What individual rights and freedoms are most important to protect?...',
                'rows': 3
            }),
            'collective_responsibilities': forms.Textarea(attrs={
                'placeholder': 'What collective duties and social responsibilities should citizens have?...',
                'rows': 3
            }),
            'cultural_considerations': forms.Textarea(attrs={
                'placeholder': 'Any specific cultural values or considerations for your network state?...',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<h4 class="mb-4"><i class="fas fa-brain text-primary me-2"></i>Define Your Political Values</h4>'),
            HTML('<p class="text-muted mb-4">These values will guide the AI in generating laws that align with your vision for your network state.</p>'),
            
            Row(
                Column('political_philosophy', css_class='form-group col-md-12 mb-3'),
                css_class='form-row'
            ),
            
            Row(
                Column('core_values', css_class='form-group col-md-6 mb-3'),
                Column('governance_style', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            
            Row(
                Column('priority_areas', css_class='form-group col-md-6 mb-3'),
                Column('economic_system', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            
            Row(
                Column('individual_rights', css_class='form-group col-md-6 mb-3'),
                Column('collective_responsibilities', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            
            Row(
                Column('cultural_considerations', css_class='form-group col-md-12 mb-3'),
                css_class='form-row'
            ),
            
            FormActions(
                Submit('submit', 'Save Values & Principles', css_class='btn btn-primary btn-lg')
            )
        )


class LawGenerationForm(forms.Form):
    """Form for generating new laws"""
    
    prompt = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Describe the law you want to create. Be specific about the problem it should solve and the outcomes you want...',
            'rows': 5,
            'class': 'form-control'
        }),
        label='Law Description',
        help_text='What kind of law do you want to create? Describe the issue, desired outcomes, and any specific requirements.'
    )
    
    category = forms.ModelChoiceField(
        queryset=LawCategory.objects.all(),
        required=False,
        empty_label='Auto-detect category',
        help_text='Leave blank to let AI suggest the best category'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<div class="law-generation-form">'),
            HTML('<h4 class="mb-3"><i class="fas fa-gavel text-primary me-2"></i>Generate New Law</h4>'),
            HTML('<div class="alert alert-info"><i class="fas fa-info-circle me-2"></i>This will cost <strong>10 credits</strong></div>'),
            
            Field('prompt', css_class='mb-3'),
            Field('category', css_class='mb-3'),
            
            FormActions(
                Submit('generate', 'Generate Law (10 Credits)', css_class='btn btn-primary btn-lg'),
                css_class='d-grid'
            ),
            HTML('</div>')
        )


class LawSearchForm(forms.Form):
    """Form for searching through generated laws"""
    
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search your laws by title, content, or tags...',
            'class': 'form-control'
        }),
        label='Search Query'
    )
    
    category = forms.ModelChoiceField(
        queryset=LawCategory.objects.all(),
        required=False,
        empty_label='All categories'
    )
    
    is_favorite = forms.BooleanField(
        required=False,
        label='Favorites only'
    )
    
    is_implemented = forms.BooleanField(
        required=False,
        label='Implemented only'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            HTML('<div class="search-form mb-4">'),
            HTML('<div class="alert alert-info"><i class="fas fa-info-circle me-2"></i>Each search costs <strong>1 credit</strong></div>'),
            
            Row(
                Column('query', css_class='col-md-6'),
                Column('category', css_class='col-md-3'),
                Column(
                    FormActions(
                        Submit('search', 'Search (1 Credit)', css_class='btn btn-primary')
                    ),
                    css_class='col-md-3 d-flex align-items-end'
                ),
                css_class='form-row'
            ),
            
            Row(
                Column('is_favorite', css_class='col-md-6'),
                Column('is_implemented', css_class='col-md-6'),
                css_class='form-row mt-2'
            ),
            
            HTML('</div>')
        )


class LawEditForm(forms.ModelForm):
    """Form for editing generated laws"""
    
    class Meta:
        model = GeneratedLaw
        fields = ['title', 'summary', 'content', 'category', 'tags', 'is_favorite', 'is_implemented', 'implementation_notes']
        
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 10}),
            'implementation_notes': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={
                'placeholder': 'Enter tags separated by commas (e.g., privacy, technology, enforcement)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<h4 class="mb-4"><i class="fas fa-edit text-primary me-2"></i>Edit Law</h4>'),
            
            Row(
                Column('title', css_class='col-md-8'),
                Column('category', css_class='col-md-4'),
                css_class='form-row'
            ),
            
            Field('summary', css_class='mb-3'),
            Field('content', css_class='mb-3'),
            Field('tags', css_class='mb-3'),
            
            Row(
                Column('is_favorite', css_class='col-md-4'),
                Column('is_implemented', css_class='col-md-4'),
                css_class='form-row'
            ),
            
            Field('implementation_notes', css_class='mb-3'),
            
            FormActions(
                Submit('save', 'Save Changes', css_class='btn btn-primary'),
                HTML('<a href="{% url "political_god:law_library" %}" class="btn btn-secondary ms-2">Cancel</a>')
            )
        )


class ConstitutionForm(forms.ModelForm):
    """Form for creating/editing state constitution"""
    
    class Meta:
        model = StateConstitution
        fields = ['name', 'preamble', 'fundamental_rights', 'governmental_structure', 'amendment_process']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., The Republic of Innovatia'
            }),
            'preamble': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'We the people of this network state, in order to...'
            }),
            'fundamental_rights': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'List the fundamental rights and freedoms...'
            }),
            'governmental_structure': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Describe how the state will be organized and governed...'
            }),
            'amendment_process': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'How can this constitution be amended in the future?...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<h4 class="mb-4"><i class="fas fa-scroll text-primary me-2"></i>State Constitution</h4>'),
            
            Field('name', css_class='mb-3'),
            Field('preamble', css_class='mb-3'),
            Field('fundamental_rights', css_class='mb-3'),
            Field('governmental_structure', css_class='mb-3'),
            Field('amendment_process', css_class='mb-3'),
            
            FormActions(
                Submit('save', 'Save Constitution', css_class='btn btn-primary'),
                Submit('generate_ai', 'Generate with AI (50 Credits)', css_class='btn btn-success ms-2')
            )
        )


class AIConstitutionForm(forms.Form):
    """Form for AI-assisted constitution generation"""
    
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., The Republic of Innovatia'
        }),
        label='State Name'
    )
    
    population = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., 10,000 citizens'
        }),
        label='Expected Population'
    )
    
    geography = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., Digital-first with physical nodes in major cities'
        }),
        label='Geographic Scope'
    )
    
    focus_areas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'e.g., Technology innovation, environmental sustainability, economic freedom'
        }),
        label='Special Focus Areas'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<h4 class="mb-4"><i class="fas fa-robot text-success me-2"></i>AI Constitution Generator</h4>'),
            HTML('<div class="alert alert-warning"><i class="fas fa-coins me-2"></i>This will cost <strong>50 credits</strong></div>'),
            
            Field('name', css_class='mb-3'),
            
            Row(
                Column('population', css_class='col-md-6'),
                Column('geography', css_class='col-md-6'),
                css_class='form-row'
            ),
            
            Field('focus_areas', css_class='mb-3'),
            
            FormActions(
                Submit('generate', 'Generate Constitution (50 Credits)', css_class='btn btn-success btn-lg'),
                css_class='d-grid'
            )
        ) 