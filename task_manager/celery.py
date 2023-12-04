from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from task.tasks import *

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_manager.settings')

app = Celery('task_manager')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/1'),  # runs every minute
        send_reminders_new.s(),
    )
    sender.add_periodic_task(
        crontab(minute='*/1'),  # runs every minute
        reminder_to_registered_user_every_morning_new.s(),
    )

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
