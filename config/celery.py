import os

from celery import Celery

# Установите переменную окружения для Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Загружаем настройки из Django с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находить задачи в приложениях Django
app.autodiscover_tasks()
