from django.urls import path
from post.views import index, NewPost, PostDetail, Tags, like, favourite
from . import views

urlpatterns = [
    path('', index, name='index'),
    path('newpost', NewPost, name='newpost'),
    path('<uuid:post_id>', PostDetail, name='post-details'),
    path('tag/<slug:tag_slug>', Tags, name='tags'),
    path('<uuid:post_id>/like', like, name='like'),
    path('<uuid:post_id>/favourite', favourite, name='favourite'),
    path('delete-post/<uuid:post_id>/', views.delete_post, name='delete-post'),
    # path('add_post/', views.add_post, name='add_post'),
    path('add_story/', views.add_story, name='add_story'),
    path('share-post/<uuid:post_id>/<int:user_id>/', views.share_post, name='share-post'),
]
