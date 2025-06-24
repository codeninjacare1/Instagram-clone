from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from directs.models import Message
from django.contrib.auth.models import User
from authy.models import Profile
from django.db.models import Q
from django.core.paginator import Paginator

@login_required
def Directs(request, username=None):
    user = request.user
    messages = Message.get_message(user=user)

    # If no username is provided, redirect to the latest chat or show an empty inbox
    if username is None:
        if messages:
            latest_chat_username = messages[0]['user'].username
            return redirect('directs', username=latest_chat_username)
        else:
            # No messages yet, show an empty inbox page but with the sidebar
            following_profiles = user.profile.following.all()
            follower_profiles = user.profile.followers.all()
            sidebar_profiles = list(set(list(following_profiles) + list(follower_profiles)))
            context = {'sidebar_users': sidebar_profiles}
            return render(request, 'directs/direct.html', context)

    # If a username is provided, proceed to show the conversation
    active_direct = username
    to_user = User.objects.get(username=username)

    # Create a consistent, shared room name for the WebSocket connection
    usernames = sorted([user.username, to_user.username])
    room_name_for_ws = f"{usernames[0]}_{usernames[1]}"

    # Fetch the full conversation history
    directs = Message.objects.filter(user=user).filter(
        Q(sender=to_user) | Q(reciepient=to_user)
    ).order_by('date')
    
    # Mark messages in this thread as read
    Message.objects.filter(user=user, reciepient=to_user, is_read=False).update(is_read=True)

    # Update unread count for the sidebar
    for message in messages:
        if message['user'].username == username:
            message['unread'] = 0

    # Sidebar users logic
    following_profiles = user.profile.following.all()
    follower_profiles = user.profile.followers.all()
    combined_profiles = set(list(following_profiles) + list(follower_profiles))
    if user.profile in combined_profiles:
        combined_profiles.remove(user.profile)
    messaged_users = {msg['user'].profile for msg in messages} if messages else set()
    sidebar_users = list(messaged_users) + [p for p in combined_profiles if p not in messaged_users]

    # Blocked logic
    user_profile = user.profile
    to_user_profile = to_user.profile
    blocked = (to_user_profile in user_profile.blocked_users.all()) or (user_profile in to_user_profile.blocked_users.all())

    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
        'blocked': blocked,
        'sidebar_users': sidebar_users,
        'room_name': room_name_for_ws
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
