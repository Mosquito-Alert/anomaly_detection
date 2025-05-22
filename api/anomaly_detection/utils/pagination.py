from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Custom pagination class for the API.
    """
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
