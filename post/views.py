from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.template import loader
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Post, Follow, Stream, Tag, Likes
from storyapp.models import Story
from .forms import NewPostform
from directs.models import Message
from authy.models import Profile
from django.contrib.auth.models import User
from post.forms import NewPostform
from authy.models import Profile
from django.urls import resolve
from comment.models import Comment
from comment.forms import NewCommentForm
from django.core.paginator import Paginator
from django.db.models import Q 
from post.models import Post, Follow, Stream
from .forms import StoryForm
from notification.models import Notification
from django.utils import timezone




@login_required
def index(request):
    user = request.user
    all_users = User.objects.all()
    
    for other_user in all_users:
        if other_user != user:
            other_user.is_followed = Follow.objects.filter(following=other_user, follower=user).exists()

    my_active_stories = Story.objects.filter(user=user, expires_at__gt=timezone.now()).order_by('-uploaded_at')
    stories = Story.objects.filter(expires_at__gt=timezone.now()).order_by('-uploaded_at')
    
    followed_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(Q(user__in=followed_users) | Q(user=request.user)).order_by('-posted')
    
    for post in posts:
        post.liked = Likes.objects.filter(user=user, post=post).exists()

    share_users = User.objects.exclude(id=request.user.id)
    unread_messages = Message.objects.filter(user=request.user, is_read=False).count()
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()

    # Add this line
    favourite_ids = request.user.profile.favourite.values_list('id', flat=True)

    # --- New: handle comment POST from index page ---
    if request.method == "POST" and 'comment_post_id' in request.POST:
        post_id = request.POST.get('comment_post_id')
        post_obj = Post.objects.get(id=post_id)
        form = NewCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post_obj
            comment.user = user
            comment.save()
            return redirect('index')

    # --- New: prepare comments and forms for each post ---
    latest_comments = {}
    comment_counts = {}
    comment_forms = {}
    for post in posts:
        comments_qs = Comment.objects.filter(post=post).order_by('-date')
        latest_comments[post.id] = list(comments_qs[:3])
        comment_counts[post.id] = comments_qs.count()
        comment_forms[post.id] = NewCommentForm()

    context = {
        'post_items': posts,
        'all_users': all_users,
        'share_users': share_users,
        'unread_messages': unread_messages,
        'notification_count': notification_count,
        'stories': stories,
        'my_active_stories': my_active_stories,
        'favourite_ids': list(favourite_ids),  # ✅ Added here
        'latest_comments': latest_comments,
        'comment_counts': comment_counts,
        'comment_forms': comment_forms,
    }

    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))


@login_required
def NewPost(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    tags_obj = []
    
    if request.method == "POST":
        form = NewPostform(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get('picture')
            caption = form.cleaned_data.get('caption')
            tag_form = form.cleaned_data.get('tags')
            tag_list = list(tag_form.split(','))

            for tag in tag_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_obj.append(t)
            p, created = Post.objects.get_or_create(picture=picture, caption=caption, user=user)
            p.tags.set(tags_obj)
            p.save()
            return redirect('profile', request.user.username)
    else:
        form = NewPostform()
    context = {
        'form': form
    }
    return render(request, 'newpost.html', context)

@login_required
def PostDetail(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-date')
    
    # Add liked status to the post
    post.liked = Likes.objects.filter(user=user, post=post).exists()

    # Get users to share posts with
    share_users = User.objects.exclude(id=request.user.id)

    if request.method == "POST":
        form = NewCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            return HttpResponseRedirect(reverse('post-details', args=[post.id]))
    else:
        form = NewCommentForm()

    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'share_users': share_users,
    }

    return render(request, 'postdetail.html', context)

@login_required
def Tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-posted')

    context = {
        'posts': posts,
        'tag': tag

    }
    return render(request, 'tag.html', context)


# Like function
@login_required
def like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    current_likes = post.likes
    liked = Likes.objects.filter(user=user, post=post).count()

    if not liked:
        Likes.objects.create(user=user, post=post)
        current_likes = current_likes + 1
    else:
        Likes.objects.filter(user=user, post=post).delete()
        current_likes = current_likes - 1
        
    post.likes = current_likes
    post.save()
    
    # Get the referrer URL to determine where to redirect
    referrer = request.META.get('HTTP_REFERER')
    if referrer and 'post-details' in referrer:
        # If coming from post details, redirect back to post details
        return HttpResponseRedirect(reverse('post-details', args=[post_id]))
    else:
        # Otherwise redirect to index
        return HttpResponseRedirect(reverse('index'))

@login_required
def favourite(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)

    if profile.favourite.filter(id=post_id).exists():
        profile.favourite.remove(post)
    else:
        profile.favourite.add(post)
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))


# def add_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST, request.FILES)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.user = request.user
#             post.save()
#             return redirect('home')
#     else:
#         form = PostForm()
#     return render(request, 'add_post.html', {'form': form})


def add_story(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.user = request.user
            story.save()
            return redirect('home')
    else:
        form = StoryForm()
    return render(request, 'add_story.html', {'form': form})

@login_required
def share_post(request, post_id, user_id):
    post = get_object_or_404(Post, id=post_id)
    recipient = get_object_or_404(User, id=user_id)
    
    # Create a message with the shared post details
    post_url = request.build_absolute_uri(reverse('post-details', args=[post.id]))
    message_body = f"View post: <a href=\"{post_url}\">{post_url}</a>"
    
    # Send the message
    Message.sender_message(request.user, recipient, message_body)
    
    messages.success(request, f'Post shared with {recipient.username}')
    return redirect('index')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the user is the owner of the post
    if request.user != post.user:
        messages.error(request, 'You are not authorized to delete this post.')
        return redirect('index')
    
    # Delete the post
    post.delete()
    messages.success(request, 'Post deleted successfully.')
    return redirect('index')

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Post

@login_required
def toggle_favourite(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile = request.user.profile

    if post in profile.favourite.all():
        profile.favourite.remove(post)
        is_fav = False
    else:
        profile.favourite.add(post)
        is_fav = True

    return JsonResponse({'favourite': is_fav})


@login_required
def save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile = request.user.profile

    if post in profile.favourite.all():
        profile.favourite.remove(post)
        is_saved = False
    else:
        profile.favourite.add(post)
        is_saved = True

    return JsonResponse({'saved': is_saved})

@require_POST
def add_comment(request, post_id):
    user = request.user
    post_obj = Post.objects.get(id=post_id)
    form = NewCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post_obj
        comment.user = user
        comment.save()
    return redirect('index')  