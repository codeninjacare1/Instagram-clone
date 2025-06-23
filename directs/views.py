from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from directs.models import Message
from django.contrib.auth.models import User
from authy.models import Profile
from django.db.models import Q
from django.core.paginator import Paginator

@login_required
def inbox(request):
    user = request.user
    messages = Message.get_message(user=request.user)
    active_direct = None
    directs = None
    profile = get_object_or_404(Profile, user=user)
    
    # Get the list of users the current user is following
    following_profiles = user.profile.following.all()
    
    # Get the list of users who follow the current user
    follower_profiles = user.profile.followers.all()

    # Combine both lists and remove duplicates
    combined_profiles = set(list(following_profiles) + list(follower_profiles))
    # Remove self if present
    combined_profiles.discard(user.profile)

    # Users with whom there is already a message
    messaged_users = set([msg['user'].profile for msg in messages]) if messages else set()

    # Sidebar users: all followers/following, but message users at the top (no duplicates)
    sidebar_users = list(messaged_users) + [p for p in combined_profiles if p not in messaged_users]

    # --- DEBUG PRINT ---
    print('Sidebar users:', [p.user.username for p in sidebar_users])

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=request.user, reciepient=message['user'])
        directs.update(is_read=True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0
    context = {
        'directs':directs,
        'messages': messages,
        'active_direct': active_direct,
        'profile': profile,
        'sidebar_users': sidebar_users,
    }
    return render(request, 'directs/direct.html', context)


@login_required
def Directs(request, username):
    user  = request.user
    messages = Message.get_message(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, reciepient__username=username)  
    directs.update(is_read=True)

    # Blocked logic
    to_user = User.objects.get(username=username)
    user_profile = user.profile
    to_user_profile = to_user.profile
    blocked = (to_user_profile in user_profile.blocked_users.all()) or (user_profile in to_user_profile.blocked_users.all())

    for message in messages:
        if message['user'].username == username:
            message['unread'] = 0

    # --- Add sidebar_users logic here ---
    following_profiles = user.profile.following.all()
    follower_profiles = user.profile.followers.all()
    combined_profiles = set(list(following_profiles) + list(follower_profiles))
    combined_profiles.discard(user.profile)
    messaged_users = set([msg['user'].profile for msg in messages]) if messages else set()
    sidebar_users = list(messaged_users) + [p for p in combined_profiles if p not in messaged_users]
    # --- End sidebar_users logic ---

    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
        'blocked': blocked,
        'sidebar_users': sidebar_users,
    }
    return render(request, 'directs/direct.html', context)

def SendDirect(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')

    if request.method == "POST":
        to_user = User.objects.get(username=to_user_username)
        Message.sender_message(from_user, to_user, body)
        return redirect('message')

def UserSearch(request):
    query = request.GET.get('q')
    context = {}
    if query:
        users = User.objects.filter(Q(username__icontains=query))

        # Paginator
        paginator = Paginator(users, 8)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

        context = {
            'users': users_paginator,
            }

    return render(request, 'directs/search.html', context)

def NewConversation(request, username):
    from_user = request.user
    body = ''
    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect('search-users')
    if from_user != to_user:
        Message.sender_message(from_user, to_user, body)
    return redirect('message')
