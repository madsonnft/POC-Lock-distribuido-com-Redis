from celery import Celery
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recebedores.settings")
django.setup()

app = Celery('recebedores')

app.conf.task_routes = {
    '*.tasks.processar_pedidos': {
        'queue': 'pedidos_recebedor'
    }
}

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
