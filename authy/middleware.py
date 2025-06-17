from django.utils import timezone
from authy.models import Profile

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            try:
                profile = Profile.objects.get(user=request.user)
                profile.last_active = timezone.now()
                profile.save()
            except Profile.DoesNotExist:
                pass
        return response 