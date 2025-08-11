from celery import shared_task
from django.conf import settings
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json
import requests
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
        data = {'chat_id': user.telegram_chat_id, 'text': message}
        requests.post(url, data=data)
    except Habit.DoesNotExist:
        pass

def schedule_habit_reminder(habit):
    """
    Создаёт или обновляет периодическую задачу для напоминания о привычке.
    """
    total_seconds = habit.time.hour * 3600 + habit.time.minute * 60 + habit.time.second
    every = habit.frequency

    # Создаём интервал
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=every,
        period=IntervalSchedule.DAYS,
    )

    # Удаляем старую задачу, если есть
    try:
        old_task = PeriodicTask.objects.get(name=f"habit_reminder_{habit.id}")
        old_task.delete()
    except PeriodicTask.DoesNotExist:
        pass

    # Создаём новую задачу
    PeriodicTask.objects.create(
        interval=schedule,
        name=f"habit_reminder_{habit.id}",
        task="tasks.send_telegram_reminder",
        args=json.dumps([habit.id]),
        start_time=habit.time,
    )