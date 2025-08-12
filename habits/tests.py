from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class PublicHabitsTest(APITestCase):
    def setUp(self):
        # Пользователи
        self.user = User.objects.create_user(username="owner", password="pass")
        self.other_user = User.objects.create_user(username="other", password="pass")
        self.anon_user = User.objects.create_user(username="anon", password="pass")

        # Аутентификация
        self.client.force_authenticate(user=self.user)

    def test_create_public_habit(self):
        """Пользователь может создать публичную привычку"""
        data = {
            "place": "парк",
            "time": "08:00:00",
            "action": "зарядка",
            "duration": 60,
            "frequency": 1,
            "is_public": True,
        }
        response = self.client.post(reverse("habit-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        habit = Habit.objects.get()
        self.assertTrue(habit.is_public)

    def test_unauthenticated_user_can_see_public_habits(self):
        """Анонимный пользователь может видеть публичные привычки"""
        Habit.objects.create(
            user=self.other_user,
            place="парк",
            time="07:00:00",
            action="кунфу",
            duration=120,
            frequency=1,
            is_public=True,
        )

        self.client.logout()
        response = self.client.get(reverse("habit-public"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "кунфу")

    def test_authenticated_user_can_see_public_habits(self):
        """Авторизованный пользователь может видеть публичные привычки"""
        Habit.objects.create(
            user=self.other_user,
            place="стадион",
            time="06:00:00",
            action="велосипед",
            duration=120,
            frequency=1,
            is_public=True,
        )

        response = self.client.get(reverse("habit-public"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_private_habits_not_in_public_list(self):
        """Приватные привычки не попадают в публичный список"""
        Habit.objects.create(
            user=self.other_user,
            place="дома",
            time="20:00:00",
            action="чтение",
            duration=60,
            frequency=1,
            is_public=False,
        )

        response = self.client.get(reverse("habit-public"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_cannot_edit_public_habit(self):
        habit = Habit.objects.create(
            user=self.other_user,
            place="парк",
            time="08:00:00",
            action="зарядка",
            duration=60,
            frequency=1,
            is_public=True,
        )

        data = {"action": "новое действие"}
        response = self.client.put(
            reverse("habit-detail", args=[habit.id]), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_public_habit(self):
        habit = Habit.objects.create(
            user=self.other_user,
            place="парк",
            time="08:00:00",
            action="зарядка",
            duration=60,
            frequency=1,
            is_public=True,
        )

        response = self.client.delete(reverse("habit-detail", args=[habit.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_edit_own_public_habit(self):
        habit = Habit.objects.create(
            user=self.user,
            place="дома",
            time="08:00:00",
            action="прыжки",
            duration=60,
            frequency=1,
            is_public=True,
        )

        data = {
            "place": "дома",
            "time": "08:00:00",
            "action": "скакать",
            "duration": 60,
            "frequency": 1,
        }
        response = self.client.put(
            reverse("habit-detail", args=[habit.id]), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit.refresh_from_db()
        self.assertEqual(habit.action, "скакать")

    def test_public_habit_appears_in_public_list(self):
        """Публичная привычка отображается в /public/"""
        Habit.objects.create(
            user=self.other_user,
            place="лес",
            time="05:00:00",
            action="ходьба",
            duration=120,
            frequency=1,
            is_public=True,
        )

        response = self.client.get(reverse("habit-public"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)
        self.assertEqual(response.data["results"][0]["action"], "ходьба")


class HabitPermissionsTest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass")
        self.other = User.objects.create_user(username="other", password="pass")

        self.habit = Habit.objects.create(
            user=self.owner,
            place="дома",
            time="08:00:00",
            action="бег",
            duration=60,
            frequency=1,
        )

    def test_user_can_only_edit_own_habit(self):
        self.client.force_authenticate(user=self.other)
        data = {"action": "плавание"}
        response = self.client.put(
            reverse("habit-detail", args=[self.habit.id]), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_only_delete_own_habit(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.delete(reverse("habit-detail", args=[self.habit.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_edit_habit(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            reverse("habit-detail", args=[self.habit.id]),
            {"action": "велосипед"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.habit.refresh_from_db()
        self.assertEqual(self.habit.action, "велосипед")
