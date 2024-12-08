from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework import status


class PaginationMixin:
    """
    Attributes:
    - page_size (int): Number of items per page. Defaults to 10 if not specified.
    - page_size_query_param (str): Query parameter to allow client to specify page size.
    - max_page_size (int): Maximum allowed page size to prevent excessive data retrieval.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request):
        """
        Paginate the given queryset based on request parameters.

        Args:
            queryset (QuerySet): The queryset to be paginated
            request (Request): The incoming HTTP request

        Returns:
            tuple: (paginated_queryset, pagination_data)
        """
        # Determine page size
        page_size = self.get_page_size(request)

        # Create paginator
        paginator = Paginator(queryset, page_size)

        # Get current page from request
        page_number = request.query_params.get('page', 1)

        try:
            # Attempt to get the specific page
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results
            page_obj = paginator.page(paginator.num_pages)

        # Prepare pagination metadata
        pagination_data = {
            'total_items': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'page_size': page_size,
            # 'has_next': page_obj.has_next(),
            # 'has_previous': page_obj.has_previous(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None
        }

        return page_obj.object_list, pagination_data

    def get_page_size(self, request):
        """
        Determine the page size based on request parameters.

        Args:
            request (Request): The incoming HTTP request

        Returns:
            int: Page size to use
        """
        # Check if page size is specified in request
        try:
            page_size = int(request.query_params.get(self.page_size_query_param, self.page_size))
            # Ensure page size doesn't exceed maximum
            return min(page_size, self.max_page_size)
        except ValueError:
            # If invalid page size, return default
            return self.page_size

    def get_paginated_response(self, data, pagination_data):
        """
        Create a paginated response with data and pagination metadata.

        Args:
            data (list): The paginated data
            pagination_data (dict): Pagination metadata

        Returns:
            Response: Paginated API response
        """
        return Response({
            'results': data,
            'pagination': pagination_data
        })
