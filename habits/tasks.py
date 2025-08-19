from datetime import datetime, timedelta

from celery import shared_task

from config.celery import app
from users.tasks import send_telegram_reminder

from .models import Habit


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Каждый день в 8:00 проверяем привычки
    sender.add_periodic_task(60.0, check_habits.s())  # каждые 60 секунд для теста


@shared_task
def check_habits():
    now = datetime.now().time()
    today = datetime.now().weekday() + 1  # Monday=1, ..., Sunday=7

    # Находим привычки, которые нужно выполнить сегодня
    habits = Habit.objects.filter(time__hour=now.hour, time__minute=now.minute)
    for habit in habits:
        days_since_last = (today - habit.created_at.weekday()) % 7
        if days_since_last % habit.frequency == 0:
            send_telegram_reminder.delay(habit.id)
