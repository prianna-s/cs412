
from django.views.generic import DetailView
from django.views.generic import UpdateView
from .models import Notification, UserProfile, CommentChallenge, CommentCompletionPost, Challenge
from .models import CompletionPost
from django.shortcuts import reverse
from .forms import UserProfileForm, CommentChallengeForm, CommentCompletionPostForm, ChallengeFilterForm
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
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


class ViewProfile(LoginRequiredMixin, DetailView):
    # View to display the user's profile. Includes feature to filter the user's challenges and completion posts.
    model = UserProfile
    template_name = 'project/profile_detail.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the logged-in user's UserProfile to the context
        context['logged_in_profile'] = UserProfile.objects.filter(user=self.request.user).first()

        # Fetch the profile of the user being viewed and the challenge filter form to filter their challenges
        form = ChallengeFilterForm(self.request.GET or None)
        profile = self.object

        # Fetch the challenges assigned to the user being viewed
        challenges = Challenge.objects.filter(
            Q(assigned_to=profile) | Q(created_by=profile)
        )

        # Fetch the completion posts for the challenges
        completion_posts = CompletionPost.objects.filter(
            challenge__in=challenges, challenge__status='Completed'
        )

        # Filter challenges based on the form inputs
        if form.is_valid():
            if form.cleaned_data.get('status'):
                challenges = challenges.filter(status=form.cleaned_data['status'])
            if form.cleaned_data.get('min_due_date'):
                challenges = challenges.filter(due_date__gte=form.cleaned_data['min_due_date'])
            if form.cleaned_data.get('max_due_date'):
                challenges = challenges.filter(due_date__lte=form.cleaned_data['max_due_date'])
            if form.cleaned_data.get('assigned_to'):
                challenges = challenges.filter(assigned_to=profile)
            if form.cleaned_data.get('created_by'):
                challenges = challenges.filter(created_by=profile)

        # Add the form and filtered challenges to the context
        context['filter_form'] = form
        context['filtered_challenges'] = challenges
        context['completion_posts'] = completion_posts

        return context
    

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    # View to update the user's profile.
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'project/profile_edit.html'

    def get_success_url(self):
        return reverse('view_profile', kwargs={'pk': self.object.pk})

class CreateCommentView(LoginRequiredMixin, CreateView):
    ## View to create a comment for a challenge.
    model = CommentChallenge
    form_class = CommentChallengeForm
    template_name = 'project/add_comment.html'

    def form_valid(self, form):
        # Populate the profile and challenge fields
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if not user_profile:
            return HttpResponseForbidden("User profile not found.")
        
        # Get the challenge ID from the request
        challenge_id = self.request.POST.get('challenge_id')
        challenge = get_object_or_404(Challenge, id=challenge_id)

        # Set the profile and challenge fields
        form.instance.profile = user_profile
        form.instance.challenge = challenge

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('challenge_detail', kwargs={'pk': self.object.challenge.pk})

class DeleteCommentView(LoginRequiredMixin, DeleteView):
    # View to delete a comment.
    model = CommentChallenge  # Or CommentPost
    template_name = 'project/comment_confirm_delete.html'

    def get_success_url(self):
        # Redirect back to the profile page after deleting the status message
        profile_id = self.object.profile.pk
        return reverse('view_profile', kwargs={'pk': profile_id})

class AddFriendView(LoginRequiredMixin, FormView):
    # View to add a friend.
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
    # View to create a challenge.
    model = Challenge
    form_class = ChallengeForm
    template_name = 'project/challenge_form.html'

    def get_form_kwargs(self):
        # Pass the logged-in user's UserProfile to the form.
        kwargs = super().get_form_kwargs()
        # Retrieve the UserProfile for the logged-in user
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            kwargs['user'] = user_profile
        return kwargs

    def form_valid(self, form):
        #Set the created_by field to the logged-in user's UserProfile.
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            form.instance.created_by = user_profile

        response = super().form_valid(form)
        
        create_challenge_notification(form.instance)

        return response
    

    def get_success_url(self):
        return reverse('news_feed')  # Redirect to the news feed after creating the challenge

    
class DeleteChallengeView(LoginRequiredMixin, DeleteView):
    # View to delete a challenge.
    model = Challenge
    template_name = 'project/challenge_confirm_delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)
    
class UpdateChallengeView(LoginRequiredMixin, UpdateView):
    # View to update a challenge.
    model = Challenge
    form_class = ChallengeForm
    template_name = 'project/challenge_edit.html'

    def get_success_url(self):
        return reverse('challenge_detail', kwargs={'pk': self.object.pk})

class CreateCompletionPostView(LoginRequiredMixin, CreateView):
    # View to create a completion post. This post indicates that a user has completed a challenge.
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
    # View to delete a completion post.
    model = CompletionPost
    template_name = 'project/completion_post_confirm_delete.html'

    def get_success_url(self):
        return reverse('news_feed')

class NewsFeedView(LoginRequiredMixin, ListView):
    # View to display the news feed.
    template_name = 'project/news_feed.html'
    context_object_name = 'feed'

    def get_queryset(self):
        # Get the logged-in user's profile
        user_profile = UserProfile.objects.get(user=self.request.user)
        # Return the news feed from the profile
        return user_profile.get_news_feed()

class NotificationView(LoginRequiredMixin, ListView):
    # View to display notifications.
    model = Notification
    template_name = 'project/notifications.html'
    context_object_name = 'notifications'  

    def get_queryset(self):
        # Fetch the logged-in user's UserProfile
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if not user_profile:
            return Notification.objects.none()  # Return empty queryset if no profile found
        return Notification.objects.filter(recipient=user_profile).order_by('-timestamp')

class ShowUsersView(ListView):
    # View to display all users. This view is used to search for users to add as friends.
    model = UserProfile
    template_name = 'project/show_all_users.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        # Get the base queryset
        queryset = super().get_queryset()

        # Get the search query
        query = self.request.GET.get('q')
        if query:
            # Filter by first name, last name, or username
            queryset = queryset.filter(
                Q(first_name__icontains=query) | 
                Q(last_name__icontains=query) | 
                Q(user__username__icontains=query)
            )

        return queryset


class ChallengeDetailView(DetailView):
    # View to display details of a challenge.
    model = Challenge
    template_name = 'project/challenge_detail.html'
    context_object_name = 'challenge'

    def get_context_data(self, **kwargs):
        # Retrieve the assigned user and comments for the challenge so both can be displayed in the template
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        context['is_assigned_user'] = (user_profile == self.object.assigned_to)
        context['comments'] = CommentChallenge.objects.filter(challenge=self.object)
        
        return context

class CompletionPostDetailView(DetailView):
    # View to display details of a completion post.
    model = CompletionPost
    template_name = 'project/completion_detail.html'
    context_object_name = 'completion_post'
    def get_context_data(self, **kwargs):
        # Retrieve the comments to be assigned in the template
        context = super().get_context_data(**kwargs)
        context['comments'] = CommentCompletionPost.objects.filter(completion_post=self.object)
        return context
       
class CreateUserProfileView(CreateView):
    # View to create a user profile.
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'project/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add an instance of UserCreationForm to the context
        context['user_form'] = UserCreationForm()
        return context

    def form_valid(self, form):
        # Save both the User and UserProfile instances

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
    # Helper Function to update the status of a challenge
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
    # Helper Function to create a notification for a challenge
    recipient = challenge.assigned_to
    message = f"NOTIFIED: {challenge.created_by.user.username} challenged you to '{challenge.title}'"
    Notification.objects.create(
        recipient=recipient,
        message=message,
        challenge=challenge,
        timestamp=timezone.now()
    )

@login_required
def like_post(request, pk):
    # Toggle like for a post (Challenge or CompletionPost)
    if 'challenge' in request.path:
        post = get_object_or_404(Challenge, id=pk)
    else:
        post = get_object_or_404(CompletionPost, id=pk)

    user_profile = UserProfile.objects.filter(user=request.user).first()

    if user_profile in post.likes.all():
        post.likes.remove(user_profile)  # Unlike the post
    else:
        post.likes.add(user_profile)  # Like the post

    return redirect(request.META.get('HTTP_REFERER', 'news_feed'))