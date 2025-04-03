from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Кастомная пагинация с параметрами 'limit' и 'page.'"""
    page_size_query_param = 'limit'
    page_query_param = 'page'
    page_size = 6
