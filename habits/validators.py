from django.core.exceptions import ValidationError


def validate_habit(habit):
    # reward и related_habit (связанные привычки) запрещены
    if habit.reward and habit.related_habit:
        raise ValidationError(
            "Нельзя указывать и вознаграждение, и связанную привычку одновременно."
        )

    # 2. Время выполнения не менее 120 мин
    if habit.duration > 120:
        raise ValidationError("Время выполнения не должно превышать 120 секунд.")

    # 3. Связанная привычка должна быть приятной
    if habit.related_habit and not habit.related_habit.is_pleasant:
        raise ValidationError("Связанная привычка должна быть приятной.")

    # 4. У приятной привычки не может быть вознаграждения или связанной привычки
    if habit.is_pleasant:
        if habit.reward:
            raise ValidationError("У приятной привычки не может быть вознаграждения.")
        if habit.related_habit:
            raise ValidationError(
                "У приятной привычки не может быть связанной привычки."
            )

    # 5. не реже 1 раза в неделю
    if habit.frequency > 7:
        raise ValidationError("Привычку нельзя выполнять реже, чем один раз в неделю.")
