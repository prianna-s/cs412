from django.shortcuts import render
from django.views.generic import ListView

# Create your views here.
from .models import Profile

class ShowAllProfilesView(ListView):
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'