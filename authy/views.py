from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse, resolve
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone

from post.models import Post, Follow, Stream
from authy.models import Profile
from .forms import EditProfileForm, UserRegisterForm
from comment.models import Comment
from storyapp.models import Story


@login_required
def UserProfile(request, username):
    # Ensure the profile exists for the logged-in user
    Profile.objects.get_or_create(user=request.user)

    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name

    if url_name == 'profile':
        posts = Post.objects.filter(user=user).order_by('-posted')
    else:
        posts = profile.favourite.all()

    # Get active stories for the user
    active_stories = Story.objects.filter(user=user, expires_at__gt=timezone.now()).order_by('-uploaded_at')

    # Profile Stats
    posts_count = posts.count()
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

    # Pagination
    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)

    context = {
        'posts': posts,
        'profile': profile,
        'posts_count': posts_count,
        'following_count': following_count,
        'followers_count': followers_count,
        'posts_paginator': posts_paginator,
        'follow_status': follow_status,
        'active_stories': active_stories,
    }
    return render(request, 'profile.html', context)


@login_required
def EditProfile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', profile.user.username)
    else:
        form = EditProfileForm(instance=profile)

    context = {
        'form': form,
    }
    return render(request, 'editprofile.html', context)


@login_required
def follow(request, username, option):
    following = get_object_or_404(User, username=username)

    try:
        f, created = Follow.objects.get_or_create(follower=request.user, following=following)

        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=request.user).delete()
        else:
            posts = Post.objects.filter(user=following)[:25]
            with transaction.atomic():
                for post in posts:
                    Stream.objects.create(
                        post=post,
                        user=request.user,
                        date=post.posted,
                        following=following
                    )

        return HttpResponseRedirect(reverse('profile', args=[username]))

    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', args=[username]))


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Hurray, your account was created!')

            # Automatically log in the user
            new_user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
            )
            login(request, new_user)

            return redirect('index')
    elif request.user.is_authenticated:
        return redirect('index')
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }
    return render(request, 'sign-up.html', context)


def logout_view(request):
    logout(request)
    return redirect('sign-in')


def sign_in(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
    if request.user.is_authenticated:
        return redirect('index')
        
    return render(request, 'sign-in.html')
