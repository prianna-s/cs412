from django.contrib import admin
from .models import UserProfile, Friend, Challenge, CompletionPost


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'profile_picture')
    search_fields = ('user__username', 'user__email')
    list_filter = ('user__is_active',)


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('profile1', 'profile2', 'timestamp')
    list_filter = ('profile1', 'profile2', 'timestamp')
    search_fields = ('profile1__user__username', 'profile2__user__username')


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'assigned_to', 'status', 'due_date')
    list_filter = ('status', 'due_date')
    search_fields = ('title', 'description', 'created_by__user__username', 'assigned_to__user__username')


@admin.register(CompletionPost)
class CompletionPostAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'photo', 'caption')
    list_filter = ('challenge__status', 'challenge__due_date')
    search_fields = ('caption', 'challenge__title', 'challenge__created_by__user__username')
