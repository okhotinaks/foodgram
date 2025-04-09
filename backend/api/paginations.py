from rest_framework.pagination import PageNumberPagination

from api.constants import PAGE_SIZE


class CustomPageNumberPagination(PageNumberPagination):
    """Кастомная пагинация с параметрами 'limit' и 'page.'"""
    page_size_query_param = 'limit'
    page_query_param = 'page'
    page_size = PAGE_SIZE
