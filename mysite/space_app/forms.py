from django import forms
from .models import User, Project, Contact, Team, Skill, Challenge
import re
import os

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    terms_and_conditions = forms.BooleanField(required=True)
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, widget=forms.RadioSelect)
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.none(),  # Use empty queryset initially
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'h-6 w-6 mr-2 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-600 ring-offset-gray-800 focus:ring-2'
        }),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'password', 'confirm_password', 'avatar',
            'national_id', 'phone_number', 'gender', 'age', 'language',
            'skills', 'organization', 'status',
            'university', 'study_field', 'medical_conditions',
            'emergency_contact', 'description', 'consent', 'terms_and_conditions'
        ]
        widgets = {
            'consent': forms.CheckboxInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills'].queryset = Skill.objects.all() # Set queryset dynamically
        self.fields['description'].label = "Past experience description (if exists)"

        text_input_class = 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': text_input_class, 'rows': '4'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': text_input_class})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-checkbox h-4 w-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-600 ring-offset-gray-800 focus:ring-2'})
            elif not isinstance(field.widget, (forms.RadioSelect, forms.FileInput, forms.CheckboxSelectMultiple)):
                field.widget.attrs.update({'class': text_input_class})

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-Z\s]+$', first_name):
            raise forms.ValidationError("First name should only contain letters and spaces.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[a-zA-Z\s]+$', last_name):
            raise forms.ValidationError("Last name should only contain letters and spaces.")
        return last_name

    def clean_organization(self):
        organization = self.cleaned_data.get('organization')
        if organization and not re.match(r'^[a-zA-Z\s]+$', organization):
            raise forms.ValidationError("Organization should only contain letters and spaces.")
        return organization

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if not re.match(r'^[a-zA-Z\s]+$', status):
            raise forms.ValidationError("Status should only contain letters and spaces.")
        return status

    def clean_study_field(self):
        study_field = self.cleaned_data.get('study_field')
        if study_field and not re.match(r'^[a-zA-Z\s]+$', study_field):
            raise forms.ValidationError("Field of study should only contain letters and spaces.")
        return study_field

    def clean_university(self):
        university = self.cleaned_data.get('university')
        if university and not re.match(r'^[a-zA-Z\s]+$', university):
            raise forms.ValidationError("University should only contain letters and spaces.")
        return university

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit() or len(phone_number) != 11:
            raise forms.ValidationError("Phone number must be 11 digits.")
        return phone_number

    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if not national_id.isdigit() or len(national_id) != 14:
            raise forms.ValidationError("National ID must be 14 digits.")
        return national_id

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and age < 12:
            raise forms.ValidationError("You must be at least 12 years old.")
        return age
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password
    
    def clean_terms_and_conditions(self):
        terms = self.cleaned_data.get('terms_and_conditions')
        if not terms:
            raise forms.ValidationError("You must accept the terms and conditions.")
        return terms

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            self.save_m2m()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text_input_class = 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': text_input_class, 'rows': '4'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-checkbox'})
            else:
                field.widget.attrs.update({'class': text_input_class})

class ProfileEditForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.none(), # Use empty queryset initially
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'avatar',
            'national_id', 'phone_number', 'gender', 'age', 'language',
            'skills', 'organization', 'status',
            'university', 'study_field', 'medical_conditions',
            'emergency_contact', 'description'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills'].queryset = Skill.objects.all() # Set queryset dynamically
        text_input_class = 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': text_input_class, 'rows': '4'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': text_input_class})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-checkbox h-4 w-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-600 ring-offset-gray-800 focus:ring-2'})
            elif not isinstance(field.widget, (forms.RadioSelect, forms.FileInput, forms.CheckboxSelectMultiple)):
                field.widget.attrs.update({'class': text_input_class})

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit() or len(phone_number) != 11:
            raise forms.ValidationError("Phone number must be 11 digits.")
        return phone_number

    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if not national_id.isdigit() or len(national_id) != 14:
            raise forms.ValidationError("National ID must be 14 digits.")
        return national_id

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and age < 12:
            raise forms.ValidationError("You must be at least 12 years old.")
        return age

class UserEditForm(forms.ModelForm):
    ROLE_CHOICES = (
        ('none', 'None'),
        ('is_admin', 'Admin'),
        ('is_moderator', 'Moderator'),
        ('is_GPE', 'GPE'),
        ('is_Mentor', 'Mentor'),
        ('is_Registration', 'Registration'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    in_team = forms.CharField(required=False, disabled=True, label="In a team")
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.none(), # Use empty queryset initially
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'skills']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills'].queryset = Skill.objects.all() # Set queryset dynamically
        user = self.instance

        if user.is_admin:
            self.fields['role'].initial = 'is_admin'
        elif user.is_moderator:
            self.fields['role'].initial = 'is_moderator'
        elif user.is_GPE:
            self.fields['role'].initial = 'is_GPE'
        elif user.is_Mentor:
            self.fields['role'].initial = 'is_Mentor'
        elif user.is_Registration:
            self.fields['role'].initial = 'is_Registration'
        else:
            self.fields['role'].initial = 'none'

        if hasattr(user, 'team_member') and user.team_member.exists():
            self.fields['in_team'].initial = "Yes"
        else:
            self.fields['in_team'].initial = "No"

        text_input_class = 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        for field_name, field in self.fields.items():
            if field_name == 'in_team':
                 field.widget.attrs.update({'class': text_input_class + ' bg-gray-600'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': text_input_class, 'rows': '4'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': text_input_class})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-checkbox h-4 w-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-600 ring-offset-gray-800 focus:ring-2'})
            elif not isinstance(field.widget, (forms.RadioSelect, forms.FileInput, forms.CheckboxSelectMultiple)):
                field.widget.attrs.update({'class': text_input_class})


    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data['role']
        user.is_admin = role == 'is_admin'
        user.is_moderator = role == 'is_moderator'
        user.is_GPE = role == 'is_GPE'
        user.is_Mentor = role == 'is_Mentor'
        user.is_Registration = role == 'is_Registration'
        
        if commit:
            user.save()
            self.save_m2m()

        return user

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'video_url', 'project_file', 'powerpoint_file', 'resources_used', 'other_notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'}),
            'description': forms.Textarea(attrs={'class': 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5', 'rows': 4}),
            'video_url': forms.URLInput(attrs={'class': 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'}),
            'project_file': forms.FileInput(attrs={'class': 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'}),
            'powerpoint_file': forms.FileInput(attrs={'class': 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'}),
            'resources_used': forms.Textarea(attrs={'class': 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5', 'rows': 4}),
            'other_notes': forms.Textarea(attrs={'class': 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            for field in self.fields.values():
                field.required = False

    def clean_powerpoint_file(self):
        powerpoint_file = self.cleaned_data.get('powerpoint_file', False)
        if powerpoint_file:
            ext = os.path.splitext(powerpoint_file.name)[1]
            valid_extensions = ['.ppt', '.pptx', '.presentation']
            if not ext.lower() in valid_extensions:
                raise forms.ValidationError('Unsupported file extension. Only .ppt, .pptx, and .presentation files are allowed.')
        return powerpoint_file

    def clean_project_file(self):
        project_file = self.cleaned_data.get('project_file', False)
        if project_file:
            ext = os.path.splitext(project_file.name)[1]
            valid_extensions = ['.rar', '.zip', '.7z']
            if not ext.lower() in valid_extensions:
                raise forms.ValidationError('Unsupported file extension. Only .rar, .zip, and .7z files are allowed.')
        return project_file

    def clean(self):
        cleaned_data = super().clean()
        
        project_data = self.instance.__dict__.copy()
        project_data.update(cleaned_data)

        if 'project_file' in self.files:
            project_data['project_file'] = self.files['project_file']
        if 'powerpoint_file' in self.files:
            project_data['powerpoint_file'] = self.files['powerpoint_file']

        required_fields = ['name', 'description', 'video_url', 'project_file', 'powerpoint_file', 'resources_used']
        
        is_complete = all(project_data.get(field) for field in required_fields)
        
        if is_complete:
            self.instance.submission_status = 'complete'
        else:
            self.instance.submission_status = 'incomplete'
            
        return cleaned_data


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text_input_class = 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': text_input_class, 'rows': '4'})
            else:
                field.widget.attrs.update({'class': text_input_class})

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'challenge', 'team_photo', 'looking_for_members']
        widgets = {
            'looking_for_members': forms.CheckboxInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['challenge'].queryset = Challenge.objects.all()
        text_input_class = 'bg-gray-700 border border-gray-600 text-white sm:text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                 field.widget.attrs.update({'class': 'form-checkbox h-4 w-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-600 ring-offset-gray-800 focus:ring-2'})
            elif not isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': text_input_class})
