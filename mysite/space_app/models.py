from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from .managers import CustomUserManager

class Challenge(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=50)
    image = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return self.title

class Skill(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('ar', 'Arabic'),
        ('fr', 'French'),
        ('de', 'German'),
        ('es', 'Spanish'),
    )
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    national_id = models.CharField(max_length=14, unique=True, validators=[MinLengthValidator(14)])
    phone_number = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.IntegerField()
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default='en')
    hackathon = models.BooleanField(default=False)
    skills = models.ManyToManyField(Skill, blank=True)
    other_skills = models.CharField(max_length=255, blank=True, help_text="List any other skills you have, separated by commas.")
    organization = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, default='active')
    university = models.CharField(max_length=255)
    study_field = models.CharField(max_length=255)
    medical_conditions = models.TextField(blank=True, null=True)
    emergency_contact = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    consent = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    terms_and_conditions = models.BooleanField(default=False)
    is_GPE = models.BooleanField(default=False)
    is_Mentor = models.BooleanField(default=False)
    is_Registration = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if self.is_GPE or self.is_Mentor or self.is_Registration:
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    @full_name.setter
    def full_name(self, name):
        first_name, last_name = name.split(' ', 1)
        self.first_name = first_name
        self.last_name = last_name


    @property
    def professional_title(self):
        return self.study_field


class Team(models.Model):
    name = models.CharField(max_length=255)
    challenge = models.ForeignKey(Challenge, on_delete=models.SET_NULL, null=True, blank=True)
    team_photo = models.ImageField(upload_to='team_photos/', null=True, blank=True)
    looking_for_members = models.BooleanField(default=True)
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    mentors = models.ManyToManyField(User, related_name='mentored_teams', blank=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams', null=True)

    def __str__(self):
        return self.name
    
    @property
    def members_count(self):
        return self.members.count()

    def join_team(self, user):
        if user.is_Mentor or user.is_admin:
            self.mentors.add(user)
        elif self.members.count() < 6:
            self.members.add(user)
        else:
            raise ValidationError("Team is full")


class Project(models.Model):
    SUBMISSION_STATUS_CHOICES = (
        ('incomplete', 'Incomplete'),
        ('complete', 'Complete'),
    )
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='project')
    name = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    project_file = models.FileField(upload_to='projects/', blank=True, null=True)
    powerpoint_file = models.FileField(upload_to='powerpoints/', blank=True, null=True)
    resources_used = models.TextField(blank=True, null=True)
    other_notes = models.TextField(blank=True, null=True)
    submission_status = models.CharField(max_length=20, choices=SUBMISSION_STATUS_CHOICES, default='incomplete')

    def __str__(self):
        return self.name

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class JoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='join_requests')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='join_requests')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} -> {self.team}'