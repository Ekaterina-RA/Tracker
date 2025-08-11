
from django.core.exceptions import ValidationError
from django.test import TestCase
from poetry.console.commands import self

from .models import Habit
from .serializers import HabitSerializer
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User

class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")

    def test_clean_duration_too_long(self):
        habit = Habit(
            user=self.user,
            place="дома",
            time="08:00:00",
            action="прыжки",
            duration=150,
            frequency=1,
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_clean_cannot_have_reward_and_related_habit(self):
        habit = Habit(
            user=self.user,
            place="дома",
            time="08:00:00",
            action="бег",
            duration=60,
            frequency=1,
            reward="кофе",
            related_habit=Habit(user=self.user, is_pleasant=True, duration=60, frequency=1),
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_clean_related_habit_must_be_pleasant(self):
        # Создаём корректную приятную привычку
        related = Habit.objects.create(
            user=self.user,
            place="дома",
            time="08:00:00",
            action="релакс",
            is_pleasant=True,
            duration=60,
            frequency=1,
        )

        habit = Habit(
            user=self.user,
            place="дома",
            time="08:00:00",
            action="бег",
            duration=60,
            frequency=1,
            related_habit=related,
        )
        habit.full_clean()  # не должно быть ошибки
        habit.save()

        # Теперь проверим, что нельзя привязать НЕ приятную
        non_pleasant = Habit.objects.create(
            user=self.user,
            place="на улице",
            time="09:00:00",
            action="ходьба",
            is_pleasant=False,
            duration=60,
            frequency=1,
        )

        habit.related_habit = non_pleasant
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_clean_pleasant_cannot_have_reward(self):
        habit = Habit(
            user=self.user,
            place="дома",
            time="08:00:00",
            action="ванны",
            duration=60,
            frequency=1,
            is_pleasant=True,
            reward="музыка",
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_frequency_too_rare(self):
        habit = Habit(
            user=self.user,
            place="дома",
            time="08:00:00",
            action="бег",
            duration=60,
            frequency=10,
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()


#views
class HabitAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.client.login(username="testuser", password="pass")
        self.client.force_authenticate(user=self.user)

    def test_create_habit(self):
        url = reverse('habit-list')
        data = {
            "place": "дома",
            "time": "08:00:00",
            "action": "прыжки",
            "duration": 60,
            "frequency": 1,
        }
        response = self.client.post(url, data)
        if response.status_code != 201:
            print("Ошибка создания привычки:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_user_can_only_see_own_habits(self):
        other_user = User.objects.create_user(username="other", password="pass")
        Habit.objects.create(user=other_user, place="там", time="08:00:00", action="бег", duration=60, frequency=1)

        response = self.client.get(reverse('habit-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
