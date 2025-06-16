from django.urls import path
from . import views

app_name = 'storyapp'

urlpatterns = [
    path('add_story/', views.AddStoryView.as_view(), name='add_story'),
    path('story/<int:pk>/', views.StoryDetailView.as_view(), name='story_detail'),
    path('delete_story/<int:pk>/', views.DeleteStoryView.as_view(), name='delete_story'),
] 