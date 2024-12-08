from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.pagination import CustomPagination


class BaseAPIView(APIView):
    @classmethod
    def success_response(cls, data=None, message=None, status_code=status.HTTP_200_OK):
        return Response({'success': True, 'message': message, 'data': data}, status=status_code)

    @classmethod
    def failure_response(cls, error=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({'success': False, 'error': error}, status=status_code)

    def get_paginated_data(self, data, request):
        page_size = request.query_params.get('page_size', 10)
        paginator = CustomPagination()
        paginator.page_size = int(page_size)
        paginated_data = paginator.paginate_queryset(data, request)
        return paginator, paginated_data
