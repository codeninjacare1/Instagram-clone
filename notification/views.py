# import imp
import importlib.util
from django.shortcuts import render, redirect
from notification.models import Notification
from django.db.models.signals import post_save, post_delete

def ShowNotification(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-date')
    
    # Mark all notifications as seen
    notifications.update(is_seen=True)

    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications/notification.html', context)

def DeleteNotification(request, noti_id):
    user = request.user
    Notification.objects.filter(id=noti_id, user=user).delete()
    return redirect('show-notification')

def user_liked_post(sender, instance, *args, **kwargs):
    like = instance
    post = like.post
    sender = like.user
    notify = Notification(post=post, sender=sender, user=post.user, notification_types=1)
    notify.save()

def user_comment_post(sender, instance, *args, **kwargs):
    comment = instance
    post = comment.post
    text_preview = comment.body[:90]
    sender = comment.user
    # Only notify if commenter is not the post owner
    if sender != post.user:
        notify = Notification(post=post, sender=sender, user=post.user, text_preview=text_preview, notification_types=2)
        notify.save()

def user_follow(sender, instance, *args, **kwargs):
    follow = instance
    sender = follow.follower
    following = follow.following
    notify = Notification(sender=sender, user=following, notification_types=3)
    notify.save()

def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_seen=False).count()
        return {'notification_count': count}
    return {'notification_count': 0}


