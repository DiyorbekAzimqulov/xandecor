# myapp/management/commands/runscheduler.py
from django.core.management.base import BaseCommand
from salesdoctorbot.scheduler import start

class Command(BaseCommand):
    help = "Starts the APScheduler."

    def handle(self, *args, **kwargs):
        start()
        self.stdout.write(self.style.SUCCESS('Scheduler started.'))
