from rest_framework import serializers

from .models import Habit


# Полный сериализатор (для владельца привычки)
class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
        }

    def validate(self, attrs):
        habit = Habit(**attrs, user=self.context['request'].user)
        habit.clean()
        return attrs


#  Сериализатор для публичных привычек (без указания места)
class HabitShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "frequency",
            "reward",
            "duration",
            "is_public",
        ]
