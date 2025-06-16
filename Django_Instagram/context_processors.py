from directs.models import Message

def unread_messages(request):
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(user=request.user, is_read=False).count()
        print(f"User {request.user.username} has {unread_count} unread messages")
        return {'unread_messages': unread_count}
    return {'unread_messages': 0} 