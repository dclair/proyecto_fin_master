import os
from celery import Celery
from celery.schedules import crontab

# Establecer la configuración predeterminada de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aficionados_network.settings')

app = Celery('aficionados_network')

# Cargar la configuración desde el objeto settings de Django usando el prefijo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descubrir tareas en todas las aplicaciones registradas en INSTALLED_APPS
app.autodiscover_tasks()

# Configuración de Celery Beat Schedule
app.conf.beat_schedule = {
    'send-event-reminders-daily-at-8am': {
        'task': 'posts.tasks.send_event_reminders_task',
        'schedule': crontab(hour=8, minute=0),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

