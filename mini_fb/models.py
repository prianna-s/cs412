from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User


class Profile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    email = models.EmailField()
    profile_image_url = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_status_messages(self):
        return self.status_messages.all().order_by('-timestamp')
    
    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})
    
    def get_friends(self):
        # Find all friendships where this profile is either profile1 or profile2
        friends_as_1 = Friend.objects.filter(profile1=self).values_list('profile2', flat=True)
        friends_as_2 = Friend.objects.filter(profile2=self).values_list('profile1', flat=True)
        
        # Combine both querysets and get the actual Profile objects
        friend_ids = list(friends_as_1) + list(friends_as_2)
        return Profile.objects.filter(id__in=friend_ids)
    
    def add_friend(self, other):
        if other not in self.get_friends() and self != other:
            Friend.objects.create(profile1=self, profile2=other)
        else:
            print(f"{other} is already a friend of {self}")
    
    def get_friend_suggestions(self):
        all_profiles = Profile.objects.exclude(id=self.id)
        friends = self.get_friends()
        return all_profiles.difference(friends)
    
    def get_news_feed(self):
        # Get all friends' profiles
        friends = self.get_friends()
        
        # Get status messages from self and all friends
        return StatusMessage.objects.filter(
            profile__in=[self.id] + list(friends.values_list('id', flat=True))
        ).order_by('-timestamp')

class StatusMessage(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='status_messages')

    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name} - {self.message[:20]} ({self.timestamp})"
    
    def get_images(self):
        return self.images.all().order_by('-timestamp')

class Image(models.Model):
    image_file = models.ImageField()
    status_message = models.ForeignKey('StatusMessage', on_delete=models.CASCADE, related_name='images')
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Image for {self.status_message.profile.first_name} {self.status_message.profile.last_name} ({self.timestamp})"
    
class Friend(models.Model):
    profile1 = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='profile1')
    profile2 = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='profile2')
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.profile1.first_name} {self.profile1.last_name} & {self.profile2.first_name} {self.profile2.last_name}"
