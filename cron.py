from django_cron import CronJobBase, Schedule
from django.utils import timezone
from storyapp.models import Story

def delete_expired_stories():
    expired_stories = Story.objects.filter(expires_at__lt=timezone.now())
    for story in expired_stories:
        story.delete()
        print(f"Deleted expired story: {story.id}")

class DeleteExpiredStoriesCronJob(CronJobBase):
    RUN_EVERY_MINS = 60  # Run every 60 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron.delete_expired_stories_job'  # A unique code to identify this job

    def do(self):
        delete_expired_stories()
        print("Cron job: Expired stories deleted.") 