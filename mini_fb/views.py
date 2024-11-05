from django.shortcuts import redirect
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from .forms import CreateProfileForm
from .models import Profile
from django.contrib.auth import authenticate, login
from .forms import CreateStatusMessageForm
from .forms import UpdateStatusMessageForm
from .forms import UpdateProfileForm
from .models import StatusMessage
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm

class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add an instance of UserCreationForm to the context
        context['user_form'] = UserCreationForm()
        return context
    
    def form_valid(self, form):
        # Recreate UserCreationForm with POST data
        user_form = UserCreationForm(self.request.POST)
        
        # Check if both forms are valid
        if user_form.is_valid():
            # Save the User form to create a new User
            user = user_form.save()
            
            # Attach the newly created user to the Profile instance
            form.instance.user = user
            
            # Save the Profile form
            self.object = form.save()
            
            # Authenticate and log in the user
            raw_password = user_form.cleaned_data.get('password1')  # Get the password
            user = authenticate(username=user.username, password=raw_password)
            if user is not None:
                login(self.request, user)  # Log in the user

            return super().form_valid(form)
        else:
            # If user_form is invalid, re-render the form with errors
            return self.form_invalid(form)



class ShowAllProfilesView(ListView):
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

class DeleteStatusMessageView(DeleteView):
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'

    def get_success_url(self):
        # Redirect back to the profile page after deleting the status message
        profile_id = self.object.profile.pk
        return reverse('show_profile', kwargs={'pk': profile_id})
    
class UpdateStatusMessageView(UpdateView):
    model = StatusMessage
    form_class = UpdateStatusMessageForm
    template_name = 'mini_fb/update_status_message.html'
    context_object_name = 'status_message'

    def get_success_url(self):
        profile_id = self.object.profile.pk
        return reverse('show_profile', kwargs={'pk': profile_id})

class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    model = StatusMessage
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(Profile, user=self.request.user)
        return context

    def form_valid(self, form):
        profile = get_object_or_404(Profile, user=self.request.user)
        form.instance.profile = profile  # Associate the status message with the profile
        return super().form_valid(form)

    def get_success_url(self):
        profile_id = self.object.profile.pk
        return reverse('show_profile', kwargs={'pk': profile_id})
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)
    
class CreateFriendView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=self.request.user)
        friend = Profile.objects.get(pk=kwargs['other_pk'])
        profile.add_friend(friend)
        profile_id = self.object.profile.pk
        return reverse('show_profile', kwargs={'pk': profile_id})
    
class FriendSuggestionsView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

class ShowNewsFeedView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)