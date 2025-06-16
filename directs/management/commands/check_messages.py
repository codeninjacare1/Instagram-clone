from django.core.management.base import BaseCommand
from directs.models import Message
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check unread messages for all users'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            unread = Message.objects.filter(user=user, is_read=False).count()
            self.stdout.write(f"User {user.username} has {unread} unread messages") 