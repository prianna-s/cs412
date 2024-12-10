from django import forms
from .models import UserProfile, Challenge, CompletionPost, CommentChallenge, CommentCompletionPost
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

class UserProfileForm(forms.ModelForm):
    # UserProfileForm for creating a new user profile
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_picture']

class ChallengeForm(forms.ModelForm):
    # For creating a new challenge
    class Meta:
        model = Challenge
        fields = ['title', 'description', 'assigned_to', 'due_date', 'image']

    def __init__(self, *args, **kwargs):
        # Passes the UserProfile of the logged-in user as the "created_by" field of the form, and limits 
        # the assigned_to choices to the user's friends
        user_profile = kwargs.pop('user', None)  # UserProfile passed via kwargs
        super().__init__(*args, **kwargs)

        if user_profile:
            # Limit assigned_to choices to the user's friends
            self.fields['assigned_to'].queryset = user_profile.get_friends()

class CompletionPostForm(forms.ModelForm):
    # For creating a new completion post
    class Meta:
        model = CompletionPost
        fields = ['caption', 'photo']

class CommentChallengeForm(forms.ModelForm):
    # For creating a new comment on a challenge
    class Meta:
        model = CommentChallenge
        fields = ['message']  

class CommentCompletionPostForm(forms.ModelForm):
    class Meta:
        model = CommentCompletionPost
        fields = ['message', 'completion_post', 'profile']

class ChallengeFilterForm(forms.Form):
    # Form for filtering challenges based on date, profile, and status. 
    STATUS_CHOICES = [('', 'Any')] + Challenge.STATUS_CHOICES

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label="Status")
    min_due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label="Due Date (From)"
    )
    max_due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label="Due Date (To)"
    )
    assigned_to = forms.BooleanField(
        required=False,
        label="Assigned to Me"
    )
    created_by = forms.BooleanField(
        required=False,
        label="Created by Me"
    )
    
