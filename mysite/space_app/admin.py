from django.contrib import admin
from .models import User, Team, Project, Contact, JoinRequest

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_GPE', 'is_Mentor', 'is_Registration')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'is_GPE', 'is_Mentor', 'is_Registration')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_Mentor or request.user.is_GPE or request.user.is_Registration

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'challenge', 'looking_for_members', 'leader')
    list_filter = ('looking_for_members', 'challenge')
    search_fields = ('name', 'challenge', 'leader__email')
    ordering = ('name',)

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_Mentor or request.user.is_GPE

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'submission_status')
    list_filter = ('team', 'submission_status')
    search_fields = ('name', 'team__name')
    ordering = ('name',)

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_Mentor or request.user.is_GPE

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    ordering = ('-created_at',)

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'status', 'created_at')
    list_filter = ('status', 'team')
    search_fields = ('user__email', 'team__name')
    ordering = ('-created_at',)
