import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_sys.settings')

app = Celery('invoice_sys')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
