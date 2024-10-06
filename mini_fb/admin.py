from django.contrib import admin

# Register your models here.
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'city', 'email', 'profile_image_url')
