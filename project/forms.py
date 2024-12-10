from django import forms
from .models import UserProfile, Challenge, CompletionPost, CommentChallenge, CommentCompletionPost
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_picture']

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['title', 'description', 'assigned_to', 'due_date', 'image']

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user', None)  # UserProfile passed via kwargs
        super().__init__(*args, **kwargs)

        if user_profile:
            # Limit assigned_to choices to the user's friends
            self.fields['assigned_to'].queryset = user_profile.get_friends()

class CompletionPostForm(forms.ModelForm):
    class Meta:
        model = CompletionPost
        fields = ['caption', 'photo']

class CommentChallengeForm(forms.ModelForm):
    class Meta:
        model = CommentChallenge
        fields = ['message', 'challenge', 'profile']

class CommentCompletionPostForm(forms.ModelForm):
    class Meta:
        model = CommentCompletionPost
        fields = ['message', 'completion_post', 'profile']