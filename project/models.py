from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.

class UserProfile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    related_name="project_profile"  # Add this line
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    

    def __str__(self):
        return self.user.username


class Friend(models.Model):
    profile1 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="friend_one")
    profile2 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="friend_two")
    timestamp = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('profile1', 'profile2')

    def __str__(self):
        return f"{self.profile1.user.username} and {self.profile2.user.username}"


class Challenge(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Expired', 'Expired'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="created_challenges")
    assigned_to = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="assigned_challenges")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    due_date = models.DateField()

    def __str__(self):
        return self.title


class CompletionPost(models.Model):
    photo = models.ImageField(upload_to='completion_photos/')
    caption = models.TextField(blank=True, null=True)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="completion_posts")
    likes = models.ManyToManyField(UserProfile, related_name="liked_posts", blank=True)

    def __str__(self):
        return f"Post for {self.challenge.title} by {self.challenge.assigned_to.user.username}"
