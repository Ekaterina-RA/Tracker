from django.db import models
from users.models import User

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    place = models.CharField(max_length=100, help_text="Укажите Ваше местонахождение")
    time = models.TimeField()
    action = models.CharField(max_length=200, help_text="Укажите Ваше действие")
    is_pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'is_pleasant': True}
    )
    frequency = models.PositiveIntegerField(default=1)
    reward = models.CharField(max_length=200, blank=True, null=True)
    duration = models.PositiveIntegerField(help_text="Продолжительность в секундах")
    is_public = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def __str__(self):
        return f"{self.action} at {self.time} in {self.place}"

    def clean(self):
        from .validators import validate_habit
        validate_habit(self)