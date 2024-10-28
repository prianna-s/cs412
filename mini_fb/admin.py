from django.contrib import admin

# Register your models here.
from .models import Profile
from .models import StatusMessage
from .models import Friend
from .models import Image

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'city', 'email', 'profile_image_url')

@admin.register(StatusMessage)
class StatusMessageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'timestamp', 'message')
    list_filter = ('profile', 'timestamp')
    search_fields = ('message',)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('status_message', 'timestamp', 'image_file')
    list_filter = ('status_message', 'timestamp')
    search_fields = ('status_message__message',)

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('profile1', 'profile2', 'timestamp')
    list_filter = ('profile1', 'profile2', 'timestamp')
    search_fields = ('profile1__first_name', 'profile1__last_name', 'profile2__first_name', 'profile2__last_name')

