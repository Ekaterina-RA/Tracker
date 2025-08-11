from rest_framework.pagination import PageNumberPagination


class HabitPagination(PageNumberPagination):
    """
    Кастомная пагинация для привычек.
    Позволяет настроить количество элементов на странице.
    """

    page_size = 5  # Количество привычек на одной странице
    page_size_query_param = "page_size"
    max_page_size = 10  # Максимальное количество элементов на странице
