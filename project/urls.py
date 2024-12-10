from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import update_challenge_status
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import update_challenge_status
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Profile URLs
    path('profile/<int:pk>/', views.ViewProfile.as_view(), name='view_profile'),  # View a user's profile
    path('profile/<int:pk>/edit/', views.UpdateProfileView.as_view(), name='edit_profile'),  # Edit profile

    # Friend Management
    path('add-friend/<int:profile_pk>/<int:other_pk>/', views.AddFriendView.as_view(), name='add_friend'),  # Add a friend

    # Challenge URLs
    path('challenges/create/', views.CreateChallengeView.as_view(), name='create_challenge'),  # Create challenge
    path('challenges/<int:pk>/update/', views.UpdateChallengeView.as_view(), name='update_challenge'),  # Update challenge
    path('challenges/<int:pk>/delete/', views.DeleteChallengeView.as_view(), name='delete_challenge'),  # Delete challenge
    path('challenges/<int:pk>/', views.ChallengeDetailView.as_view(), name='challenge_detail'),  

    # Completion Post URLs
    path('completion-posts/create/', views.CreateCompletionPostView.as_view(), name='create_completion_post'),  # Create completion post
    path('completion-posts/<int:pk>/delete/', views.DeleteCompletionPostView.as_view(), name='delete_completion_post'),  # Delete completion post
    path('completion-posts/<int:pk>/', views.CompletionPostDetailView.as_view(), name='completion_post_detail'),  # View completion post
    
    # Comment URLs
    path('comments/create/', views.CreateCommentView.as_view(), name='create_comment'),  # Create comment
    path('comments/<int:pk>/delete/', views.DeleteCommentView.as_view(), name='delete_comment'),  # Delete comment

    # News Feed and Notifications
    path('news-feed/', views.NewsFeedView.as_view(), name='news_feed'),  # News feed
    path('', views.ShowUsersView.as_view(), name='all_users'),  # All profiles
    path('notifications/', views.NotificationView.as_view(), name='notifications'),  # Notifications

    path('register/', views.CreateUserProfileView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='project/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='project/logout.html'), name='logout'),
    path('challenges/<int:pk>/update_status/', update_challenge_status, name='update_challenge_status'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
