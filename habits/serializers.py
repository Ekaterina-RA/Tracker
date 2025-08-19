from rest_framework import serializers

from .models import Habit


# Полный сериализатор (для владельца привычки)
class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True},
        }

    def validate(self, attrs):
        # Только если передано поле duration
        if "duration" in attrs and attrs["duration"] > 120:
            raise serializers.ValidationError(
                {"duration": "Время выполнения не должно превышать 120 секунд."}
            )

        # Только если reward и related_habit оба переданы
        if "reward" in attrs and "related_habit" in attrs:
            if attrs["reward"] and attrs["related_habit"]:
                raise serializers.ValidationError(
                    {
                        "reward": "Нельзя указывать и вознаграждение, и связанную привычку одновременно.",
                        "related_habit": "Нельзя указывать и вознаграждение, и связанную привычку одновременно.",
                    }
                )

        # Проверка связанной привычки (если она передана)
        if "related_habit" in attrs and attrs["related_habit"]:
            if not attrs["related_habit"].is_pleasant:
                raise serializers.ValidationError(
                    {"related_habit": "Связанная привычка должна быть приятной."}
                )

        # Проверка приятной привычки
        if "is_pleasant" in attrs and attrs["is_pleasant"]:
            if "reward" in attrs and attrs["reward"]:
                raise serializers.ValidationError(
                    {"reward": "У приятной привычки не может быть вознаграждения."}
                )
            if "related_habit" in attrs and attrs["related_habit"]:
                raise serializers.ValidationError(
                    {
                        "related_habit": "У приятной привычки не может быть связанной привычки."
                    }
                )

        # Проверка частоты
        if "frequency" in attrs and attrs["frequency"] > 7:
            raise serializers.ValidationError(
                {"frequency": "Привычку нельзя выполнять реже, чем раз в 7 дней."}
            )

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
