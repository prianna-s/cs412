
from django.views.generic import DetailView
from django.views.generic import UpdateView
from .models import Notification, UserProfile, CommentChallenge, CommentCompletionPost, Challenge
from .models import CompletionPost
from django.shortcuts import reverse
from .forms import UserProfileForm, CommentChallengeForm, CommentCompletionPostForm 
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import FormView, ListView
from .forms import ChallengeForm, CompletionPostForm
from itertools import chain
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone


class ViewProfile(DetailView):
    model = UserProfile
    template_name = 'project/profile_detail.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the logged-in user's UserProfile to the context
        context['logged_in_profile'] = UserProfile.objects.filter(user=self.request.user).first()
        return context

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'project/profile_edit.html'

    def get_success_url(self):
        return reverse('view_profile', kwargs={'pk': self.object.pk})

class CreateCommentView(LoginRequiredMixin, CreateView):
    model = CommentChallenge  # Or CommentCompletionPost
    form_class = CommentChallengeForm  # Adjust for CommentCompletionPost
    template_name = 'project/comment_form.html'

    def get_success_url(self):
        return reverse('challenge_detail', kwargs={'pk': self.object.challenge.pk})

class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = CommentChallenge  # Or CommentPost
    template_name = 'project/comment_confirm_delete.html'

    def get_success_url(self):
        # Redirect back to the profile page after deleting the status message
        profile_id = self.object.profile.pk
        return reverse('view_profile', kwargs={'pk': profile_id})

class AddFriendView(LoginRequiredMixin, FormView):
    def dispatch(self, request, *args, **kwargs):
        # Retrieve the logged-in user's profile
        profile = get_object_or_404(UserProfile, pk=kwargs['profile_pk'], user=request.user)

        # Retrieve the target friend's profile
        friend = get_object_or_404(UserProfile, pk=kwargs['other_pk'])

        # Add the friend
        profile.add_friend(friend)

        # Redirect to the friend's profile
        return redirect('view_profile', pk=friend.pk)


class CreateChallengeView(LoginRequiredMixin, CreateView):
    model = Challenge
    form_class = ChallengeForm
    template_name = 'project/challenge_form.html'

    def get_form_kwargs(self):
        """Pass the logged-in user's UserProfile to the form."""
        kwargs = super().get_form_kwargs()
        # Retrieve the UserProfile for the logged-in user
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            kwargs['user'] = user_profile
        return kwargs

    def form_valid(self, form):
        """Set the created_by field to the logged-in user's UserProfile."""
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            form.instance.created_by = user_profile

        response = super().form_valid(form)
        
        create_challenge_notification(form.instance)

        return response
    

    def get_success_url(self):
        return reverse('news_feed')  # Redirect to the news feed after creating the challenge

    
class DeleteChallengeView(LoginRequiredMixin, DeleteView):
    model = Challenge
    template_name = 'project/challenge_confirm_delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)
    
class UpdateChallengeView(LoginRequiredMixin, UpdateView):
    model = Challenge
    form_class = ChallengeForm
    template_name = 'project/challenge_edit.html'

    def get_success_url(self):
        return reverse('challenge_detail', kwargs={'pk': self.object.pk})

class CreateCompletionPostView(LoginRequiredMixin, CreateView):
    model = CompletionPost
    form_class = CompletionPostForm
    template_name = 'project/completion_form.html'

    def form_valid(self, form):
        # Link the completion post to the challenge
        challenge_id = self.request.GET.get('challenge_id')
        challenge = get_object_or_404(Challenge, id=challenge_id)

        # Ensure only the assigned user can create a completion post
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if not user_profile:
            return HttpResponseForbidden("User profile not found.")

        # Mark the challenge as completed
        challenge.status = 'Completed'
        challenge.completed_on = timezone.now()
        challenge.save()

        # Save the completion post
        form.instance.challenge = challenge
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('challenge_detail', kwargs={'pk': self.object.challenge.id})


class DeleteCompletionPostView(LoginRequiredMixin, DeleteView):
    model = CompletionPost
    template_name = 'project/completion_post_confirm_delete.html'

    def get_success_url(self):
        return reverse('news_feed')

class NewsFeedView(LoginRequiredMixin, ListView):
    template_name = 'project/news_feed.html'
    context_object_name = 'feed'

    def get_queryset(self):
        # Get the logged-in user's profile
        user_profile = UserProfile.objects.get(user=self.request.user)
        # Return the news feed from the profile
        return user_profile.get_news_feed()

class NotificationView(LoginRequiredMixin, ListView):
    model = UserProfile
    template_name = 'project/notifications.html'
    context_object_name = 'profile'

    def get_queryset(self):
        # Fetch the logged-in user's UserProfile
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        return Notification.objects.filter(recipient=user_profile).order_by('-timestamp')
    
class ShowUsersView(ListView):
    model = UserProfile
    template_name = 'project/show_all_users.html'
    context_object_name = 'profiles'

class ChallengeDetailView(DetailView):
    model = Challenge
    template_name = 'project/challenge_detail.html'
    context_object_name = 'challenge'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        context['is_assigned_user'] = (user_profile == self.object.assigned_to)
        context['comments'] = CommentChallenge.objects.filter(challenge=self.object)
        
        return context

class CompletionPostDetailView(DetailView):
    model = CompletionPost
    template_name = 'project/completion_detail.html'
    context_object_name = 'completion_post'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = CommentCompletionPost.objects.filter(completion_post=self.object)
        return context
       
class CreateUserProfileView(CreateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'project/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add an instance of UserCreationForm to the context
        context['user_form'] = UserCreationForm()
        return context

    def form_valid(self, form):
        '''Save both the User and the UserProfile.'''
        # Reconstruct the UserCreationForm from POST data
        user_form = UserCreationForm(self.request.POST)

        if user_form.is_valid():
            # Save the new User and get the instance
            user = user_form.save()

            # Attach the User to the Profile instance
            form.instance.user = user
            form.instance.email = user.email  # Assign the email from the User

            self.object = form.save()

            login(self.request, user)

            # Save the Profile and redirect
            return super().form_valid(form)
        else:
            # If the UserCreationForm is invalid, re-render the page with errors
            return self.form_invalid(form)
        
    
def update_challenge_status(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)

    # Check if the logged-in user is allowed to update the challenge
    if request.user != challenge.created_by.user and request.user != challenge.assigned_to.user:
        return HttpResponseForbidden("You are not authorized to update this challenge.")

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Challenge.STATUS_CHOICES).keys():
            challenge.status = status
            challenge.save()
            return redirect('challenge_detail', pk=pk)

    return redirect('challenge_detail', pk=pk)

def create_challenge_notification(challenge):
    """Create a notification for the assigned user."""
    recipient = challenge.assigned_to
    message = f"NOTIFIED: {challenge.created_by.user.username} challenged you to '{challenge.title}'"
    Notification.objects.create(
        recipient=recipient,
        message=message,
        challenge=challenge,
        timestamp=timezone.now()
    )