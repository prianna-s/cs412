from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils import timezone
from django.shortcuts import reverse
from itertools import chain
from django.db.models import Sum


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
    
    def get_friends(self):
        # Find all friendships where this profile is either profile1 or profile2
        friends_as_1 = Friend.objects.filter(profile1=self).values_list('profile2', flat=True)
        friends_as_2 = Friend.objects.filter(profile2=self).values_list('profile1', flat=True)

        friend_ids = list(friends_as_1) + list(friends_as_2)
        return UserProfile.objects.filter(id__in=friend_ids)
    
    def add_friend(self, other):
        # Add a friend relationship between this profile and another profile
        if other not in self.get_friends() and self != other:
            Friend.objects.create(profile1=self, profile2=other)
        else:
            print(f"{other} is already a friend of {self}")

    def get_challenges(self):
        # Return a queryset of all challenges created by this user
        return Challenge.objects.filter(created_by=self)
    
    def get_challenged(self):
        # Return a queryset of all challenges assigned to this user
        return Challenge.objects.filter(assigned_to=self)
    
    def get_notifications(self):
        # Return a queryset of all notifications for this user
        return Notification.objects.filter(recipient=self)
    
    def get_absolute_url(self):
        return reverse('view_profile', kwargs={'pk': self.pk})
    
    def get_news_feed(self):
        # Return a queryset of all status messages, challenges, and completion posts
        # Get all friends' profiles
        friends = self.get_friends()

        # Get all challenges created by self and friends
        challenges = Challenge.objects.filter(
            created_by__in=[self] + list(friends)
        )

        # Get all completion posts related to challenges by self and friends
        completion_posts = CompletionPost.objects.filter(
            challenge__created_by__in=[self] + list(friends)
        )

    # Add content type to distinguish items
        challenges = challenges.annotate(content_type=models.Value('challenge', output_field=models.CharField()))
        completion_posts = completion_posts.annotate(content_type=models.Value('completion_post', output_field=models.CharField()))

    # Combine challenges and completion posts
        news_feed = sorted(
            chain(challenges, completion_posts),
            key=lambda x: x.created_at,  # Assuming both models have a `created_at` field
            reverse=True
        )

        return news_feed
    
    def calculate_score(self):
        # Get challenges created and assigned

        # Total likes on completion posts
        completed_challenges = Challenge.objects.filter(assigned_to=self, status='Completed')
        created_challenges_likes = Challenge.objects.filter(created_by=self).aggregate(total_likes=Sum('likes'))['total_likes'] or 0

        # Calculate average completion time for assigned challenges
        completion_posts = CompletionPost.objects.filter(challenge__assigned_to=self)
        completion_post_likes = completion_posts.aggregate(total_likes=Sum('likes'))['total_likes'] or 0

        completion_times = [challenge.completion_time() for challenge in completed_challenges if challenge.completion_time() is not None]
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

        # Heuristic: weighted score
        score = (
            len(completed_challenges) * 10 +  # 10 points per completed challenge
            max(0, (30 - avg_completion_time) * 5) +  # Faster completion adds more points, capped
            created_challenges_likes * 2 +  # 2 points per like on created challenges
            completion_post_likes * 3  # 3 points per like on completion posts
        )
        return round(score, 2)  # Return a rounded score
    
class CommentChallenge(models.Model):
    # Model to leave comments on challenges
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    challenge = models.ForeignKey('Challenge', on_delete=models.CASCADE)
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comment_challenges')

    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name} - {self.message[:20]} ({self.timestamp})"

class CommentCompletionPost(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    completion_post = models.ForeignKey('CompletionPost', on_delete=models.CASCADE)
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comment_completion_posts')

    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name} - {self.message[:20]} ({self.timestamp})"
    

class Friend(models.Model):
    # A friend relationship is a many-to-many relationship between two UserProfiles
    profile1 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="friend_one")
    profile2 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="friend_two")
    timestamp = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('profile1', 'profile2')

    def __str__(self):
        return f"{self.profile1.user.username} and {self.profile2.user.username}"


class Challenge(models.Model):
    # A challenge is created by one user and assigned to another to complete
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
    completed_on = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)  # New field
    likes = models.ManyToManyField(UserProfile, related_name="liked_challenges", blank=True)  # Add likes field
    
    def __str__(self):
        return self.title
    
    def total_likes(self):
        return self.likes.count()
    
    def get_comments(self):
        # Returns a list of comments for this challenge
        return CommentChallenge.objects.filter(challenge=self)
    
    def mark_expired_challenges():
         #Marks challenges that have expired as 'Expired'
        expired_challenges = Challenge.objects.filter(due_date__lt=timezone.now(), status='Pending')
        expired_challenges.update(status='Expired')

    def mark_as_completed(self):
        #Marks the challenge as completed and records the completion date.
        if self.status == 'Pending':
            self.status = 'Completed'
            self.completed_on = now().date()
            self.save()
        else:
            raise ValueError("Only challenges with 'Pending' status can be marked as completed.")
    
    def is_completed(self):
        #Checks if the challenge is completed. 
        if self.status == 'Completed':
            return True
        else:
            return False
        
    def completion_time(self):
        #Calculates the time taken to complete the challenge.
        if self.completed_on and self.status == 'Completed':
            return (self.completed_on - self.created_at.date()).days
        return None




class CompletionPost(models.Model):
    ## A completion post is created by the user who completed the challenge. It displays the photo and caption to prove completion.
    photo = models.ImageField(upload_to='images/', blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="completion_posts")
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(UserProfile, related_name="liked_completion_posts", blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Post for {self.challenge.title} by {self.challenge.assigned_to.user.username}"
    
    def get_comments(self):
        return CommentCompletionPost.objects.filter(completion_post=self)

class Notification(models.Model):
    # A notification is created when a challenge is assigned. It  is sent to the assigned user.
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="recipient")
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.recipient.user.username} - {self.message} - {self.challenge}"