import json

from celery import shared_task
from celery.worker.state import requests
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from config import settings
from habits.models import Habit


@shared_task
def send_telegram_reminder(habit_id):
    try:
        habit = Habit.objects.get(id=habit_id)
        user = habit.user
        if not user.telegram_chat_id:
            return

        message = (
            f"Напоминание: пора выполнить привычку!\n"
            f"{habit.action}\n"
            f"{habit.place}\n"
            f"{habit.time.strftime('%H:%M')}"
        )

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": user.telegram_chat_id, "text": message}
        requests.post(url, data=data)
    except Habit.DoesNotExist:
        pass


def schedule_habit_reminder(habit):
    time = habit.time

    # Создаём crontab: каждый день в habit.time
    schedule, created = CrontabSchedule.objects.get_or_create(
        hour=time.hour,
        minute=time.minute,
        day_of_week="*",
        month_of_year="*",
        day_of_month="*",
    )

    # Удаляем старую задачу
    PeriodicTask.objects.filter(name=f"habit_reminder_{habit.id}").delete()

    # Создаём новую
    PeriodicTask.objects.create(
        crontab=schedule,
        name=f"habit_reminder_{habit.id}",
        task="tasks.send_telegram_reminder",
        args=json.dumps([habit.id]),
    )
