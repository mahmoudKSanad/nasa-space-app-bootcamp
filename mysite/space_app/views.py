import json
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth import login, logout, authenticate
from .forms import RegistrationForm, LoginForm, ProjectForm, ContactForm, ProfileEditForm, UserEditForm, TeamForm
from .models import User, Team, Project, Contact, JoinRequest, Skill
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count
from django.contrib import messages

def is_GPE(user):
    return user.is_authenticated and user.is_GPE

def is_Mentor(user):
    return user.is_authenticated and user.is_Mentor

def is_Registration(user):
    return user.is_authenticated and user.is_Registration

def is_admin(user):
    return user.is_authenticated and user.is_admin

def is_moderator(user):
    return user.is_authenticated and user.is_moderator

@login_required
def dashboard_redirect_view(request):
    user = request.user
    if user.is_admin or user.is_moderator or user.is_GPE or user.is_Mentor or user.is_Registration:
        return redirect('admin_dashboard')
    return redirect('profile')

def landing_page(request):
    return render(request, 'space_app/landing_page.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('profile')
        else:
            messages.error(request, 'Unsuccessful registration. Invalid information.')
    else:
        form = RegistrationForm()
    return render(request, 'space_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard_redirect')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'space_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing_page')

@login_required
def profile_view(request):
    team = request.user.teams.first()
    project = None
    if team:
        try:
            project = team.project
        except Project.DoesNotExist:
            project = None

    return render(request, 'space_app/profile.html', {'project': project, 'team': team})

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin or u.is_moderator or u.is_GPE or u.is_Mentor or u.is_Registration))
def participant_dashboard(request):
    users = User.objects.all()
    query = request.GET.get('q')
    if query:
        users = users.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))
    return render(request, 'space_app/participant_dashboard.html', {'users': users})

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin or u.is_moderator or u.is_GPE or u.is_Mentor))
def admin_dashboard(request):
    users = User.objects.prefetch_related('teams').all()
    teams = Team.objects.all()
    projects = Project.objects.all()
    contacts = Contact.objects.all()

    query = request.GET.get('q')
    role_filter = request.GET.get('role')
    in_team_filter = request.GET.get('in_team')

    if query:
        users = users.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))

    if role_filter:
        if role_filter == 'admin':
            users = users.filter(is_admin=True)
        elif role_filter == 'gpe':
            users = users.filter(is_GPE=True)
        elif role_filter == 'mentor':
            users = users.filter(is_Mentor=True)
        elif role_filter == 'registration':
            users = users.filter(is_Registration=True)
        elif role_filter == 'moderator':
            users = users.filter(is_moderator=True)
        elif role_filter == 'user':
            users = users.filter(is_admin=False, is_GPE=False, is_Mentor=False, is_Registration=False, is_moderator=False)

    if in_team_filter:
        if in_team_filter == 'yes':
            users = users.filter(teams__isnull=False).distinct()
        elif in_team_filter == 'no':
            users = users.filter(teams__isnull=True).distinct()

    context = {
        'users': users,
        'teams': teams,
        'projects': projects,
        'contacts': contacts,
        'query': query,
        'role_filter': role_filter,
        'in_team_filter': in_team_filter,
    }
    return render(request, 'space_app/admin_dashboard.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'space_app/edit_profile.html', {'form': form})

@user_passes_test(is_admin)
def edit_user(request, user_id):
    user_to_edit = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, 'User details updated successfully.')
            return redirect('admin_dashboard')
    else:
        form = UserEditForm(instance=user_to_edit)
    return render(request, 'space_app/edit_user.html', {'form': form, 'user_to_edit': user_to_edit})

@user_passes_test(is_admin)
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, pk=user_id)
    user_to_delete.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('admin_dashboard')

@login_required
def create_team(request):
    if request.user.teams.exists():
        messages.error(request, 'You are already in a team and cannot create a new one.')
        return redirect('profile')
    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES)
        if form.is_valid():
            if not form.cleaned_data['challenge']:
                messages.error(request, 'Please select a challenge before creating a team.')
            else:
                team = form.save(commit=False)
                team.leader = request.user
                team.save()
                team.members.add(request.user)
                messages.success(request, 'Team created successfully!')
                return redirect('team_detail', team_id=team.id)
    else:
        form = TeamForm()
    return render(request, 'space_app/create_team.html', {'form': form})

@login_required
def edit_team(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    if not (request.user.is_admin or request.user == team.leader):
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('team_detail', team_id=team.id)

    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, 'Team updated successfully.')
            return redirect('team_detail', team_id=team.id)
    else:
        form = TeamForm(instance=team)
    return render(request, 'space_app/edit_team.html', {'form': form, 'team': team})

@login_required
def create_project(request, team_id):
    team = get_object_or_404(Team, pk=team_id, members=request.user)
    if hasattr(team, 'project'):
        messages.error(request, 'This team already has a project.')
        return redirect('team_detail', team_id=team.id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.team = team
            project.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, 'space_app/create_project.html', {'form': form, 'team': team})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    team_members = project.team.members.all()

    if not (request.user.is_admin or request.user in team_members):
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('project_detail', project_id=project.id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'space_app/edit_project.html', {'form': form, 'project': project})

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    team_.id = project.team.id
    if not (request.user.is_admin or request.user in project.team.members.all()):
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('project_detail', project_id=project.id)
    project.delete()
    messages.success(request, 'Project deleted successfully.')
    if request.user.is_admin:
        return redirect('admin_dashboard')
    return redirect('team_detail', team_id=team_id)

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'space_app/project_detail.html', {'project': project})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            send_mail(
                'New Contact Message',
                'You have a new message from the contact form.',
                'from@example.com',
                ['admin@example.com'],
                fail_silently=False,
            )
            return redirect('contact_success')
    else:
        form = ContactForm()
    return render(request, 'space_app/contact.html', {'form': form})

def contact_success(request):
    return render(request, 'space_app/contact_success.html')

def about_us(request):
    with open('mysite/space_app/data/committees.json', 'r') as f:
        committees_data = json.load(f)
    return render(request, 'space_app/about_us.html', committees_data)

def privacy_policy(request):
    return render(request, 'space_app/privacy_policy.html')

def rules(request):
    return render(request, 'space_app/rules.html')

def parse_description(description):
    sections = []
    current_section = None
    for line in description.splitlines():
        line = line.strip()
        if line.startswith('■'):
            if current_section:
                sections.append(current_section)
            current_section = {'title': line.strip('■ '), 'content': []}
        elif line.startswith(('-', '*')):
            if current_section:
                current_section['content'].append({'type': 'list', 'text': line.strip('-* ')})
        elif '(Display inside a styled card/box for emphasis)' in line:
            if current_section:
                current_section['is_card'] = True
        elif line:
            if current_section:
                current_section['content'].append({'type': 'paragraph', 'text': line})
    if current_section:
        sections.append(current_section)
    return sections

def challenges(request):
    with open('mysite/space_app/data/challenges.json', 'r') as f:
        challenges_data = json.load(f)
    for challenge in challenges_data:
        challenge['parsed_description'] = parse_description(challenge['description'])
    return render(request, 'space_app/challenges.html', {'challenges': challenges_data})

@login_required
def delete_team(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    if request.user != team.leader and not request.user.is_admin:
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('teams')
    team.delete()
    messages.success(request, 'Team deleted successfully.')
    return redirect('teams')

def teams(request):
    teams = Team.objects.annotate(num_members=Count('members')).filter(num_members__gt=0)
    query = request.GET.get('q')
    if query:
        teams = teams.filter(
            Q(name__icontains=query) | Q(challenge__icontains=query)
        )
    
    pending_request_team_ids = []
    if request.user.is_authenticated:
        pending_request_team_ids = list(JoinRequest.objects.filter(user=request.user, status='pending').values_list('team__id', flat=True))

    context = {
        'teams': teams,
        'pending_request_team_ids': pending_request_team_ids
    }
    return render(request, 'space_app/teams.html', context)

def team_detail(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    has_pending_request = False
    if request.user.is_authenticated:
        has_pending_request = JoinRequest.objects.filter(user=request.user, team=team, status='pending').exists()
    
    context = {
        'team': team,
        'has_pending_request': has_pending_request
    }
    return render(request, 'space_app/team_detail.html', context)

@login_required
def join_team(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    user = request.user

    if user.is_admin or user.is_Mentor:
        if user in team.mentors.all():
            messages.info(request, 'You are already a mentor for this team.')
        else:
            team.mentors.add(user)
            messages.success(request, 'You have been added as a mentor to this team.')
        return redirect('teams')

    if user.teams.exists():
        messages.error(request, 'You must leave your current team before joining a new one.')
        return redirect('teams')

    if team.members.count() >= 6:
        messages.error(request, 'This team is full and cannot accept new members.')
        return redirect('teams')

    if JoinRequest.objects.filter(user=user, team=team, status='pending').exists():
        messages.error(request, 'You have already sent a request to join this team.')
        return redirect('teams')

    if team.looking_for_members:
        JoinRequest.objects.create(user=user, team=team)
        messages.success(request, 'Your request to join the team has been sent.')
    else:
        messages.error(request, 'This team is not looking for members.')
    
    return redirect('teams')

@login_required
def cancel_join_request(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    join_request = get_object_or_404(JoinRequest, user=request.user, team=team, status='pending')
    join_request.delete()
    messages.success(request, 'Your join request has been canceled.')
    return redirect('teams')

@login_required
def leave_team(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    if request.user in team.members.all():
        team.members.remove(request.user)
        if team.leader == request.user:
            if team.members.count() > 0:
                team.leader = team.members.first()
                team.save()
            else:
                team.delete()
                messages.success(request, f'The team {team.name} has been deleted as it has no members left.')
                return redirect('profile') 
        messages.success(request, f'You have left the team {team.name}.')
    else:
        messages.error(request, 'You are not a member of this team.')
    return redirect('profile')

@login_required
def invite_member(request, team_id):
    return redirect('profile')

@login_required
def manage_join_requests(request, team_id):
    team = get_object_or_404(Team, pk=team_id, leader=request.user)
    join_requests = JoinRequest.objects.filter(team=team, status='pending')
    return render(request, 'space_app/manage_join_requests.html', {'team': team, 'requests': join_requests})

@login_required
def handle_join_request(request, request_id, action):
    join_request = get_object_or_404(JoinRequest, pk=request_id)
    team = join_request.team
    if request.user != team.leader:
        messages.error(request, 'You are not authorized to perform this action.')
        return redirect('profile')

    if action == 'accept':
        if team.members.count() >= 6:
            messages.error(request, 'The team is full and cannot accept new members.')
            return redirect('manage_join_requests', team_id=team.id)

        join_request.status = 'accepted'
        team.members.add(join_request.user)
        messages.success(request, f'{join_request.user.first_name} {join_request.user.last_name} has been added to the team.')
        JoinRequest.objects.filter(user=join_request.user, status='pending').delete()
    elif action == 'reject':
        join_request.status = 'rejected'
        messages.success(request, f"{join_request.user.first_name} {join_request.user.last_name}'s request has been rejected.")
    
    join_request.save()
    return redirect('manage_join_requests', team_id=team.id)

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin or u.is_moderator or u.is_GPE or u.is_Mentor))
def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'space_app/user_detail.html', {'user': user})