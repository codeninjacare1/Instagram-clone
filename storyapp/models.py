from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ImageField(upload_to='stories/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    viewed_by = models.ManyToManyField(User, related_name='viewed_stories', blank=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + datetime.timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"Story by {self.user.username}"
