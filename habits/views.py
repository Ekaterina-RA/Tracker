from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from users.tasks import schedule_habit_reminder

from .models import Habit
from .paginator import HabitPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import HabitSerializer, HabitShortSerializer


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = HabitPagination

    def get_queryset(self):
        if self.action == "public":
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        habit = serializer.save(user=self.request.user)
        schedule_habit_reminder(habit)

    def perform_update(self, serializer):
        habit = serializer.save()
        schedule_habit_reminder(habit)

    def get_serializer_class(self):
        if self.action == "public":
            return HabitShortSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def public(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
