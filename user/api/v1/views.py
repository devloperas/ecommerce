from django.db.models import Q
from django.utils.timezone import now
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework import status, permissions

from django.contrib.auth.tokens import PasswordResetTokenGenerator

from basics.api.v1.views import BaseAPIView
from user.api.v1.serializers import ResetPasswordRequestSerializer, ResetPasswordSerializer, UserSerializer
from user.models import User
from drf_yasg.utils import swagger_auto_schema


class UserListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

# class UserListView(BaseAPIView):
#     permission_classes = [permissions.AllowAny]
#
#     def get(self, request, *args, **kwargs):
#         # Get all users
#         queryset = User.objects.all()
#
#         # Apply custom pagination
#         paginator = CustomPagination()
#         paginated_queryset = paginator.paginate_queryset(queryset, request)
#         serializer = UserSerializer(paginated_queryset, many=True)
#
#         # Return the paginated response
#         return self.success_response(
#                     data=paginator.get_paginated_response(serializer.data),
#                     message="User list retrieved successfully"
#                 )
        # return paginator.get_paginated_response(serializer.data)

# class UserListView(BaseAPIView, PaginationMixin):
#     permission_classes = [permissions.AllowAny]
#     """
#     View for listing users with pagination.
#     """
#
#     def get(self, request, *args, **kwargs):
#         # Get all users
#         queryset = User.objects.all()
#
#         # Filter or search logic (optional, based on query parameters)
#         search_query = request.query_params.get('search', None)
#         if search_query:
#             queryset = queryset.filter(
#                 Q(first_name__icontains=search_query) |
#                 Q(last_name__icontains=search_query) |
#                 Q(email__icontains=search_query)
#             )
#
#         # Apply pagination
#         paginated_queryset, pagination_data = self.paginate_queryset(queryset, request)
#
#         # Serialize paginated data
#         serializer = UserSerializer(paginated_queryset, many=True)
#
#         # Create response
#         return self.success_response(
#             data={
#                 'users': serializer.data,
#                 'pagination': pagination_data
#             },
#             message="User list retrieved successfully"
#         )


class UserCreateView(BaseAPIView):
    """View for creating a new user."""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=UserSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            _user = serializer.save()
            return self.success_response(serializer.data, message="User Registered Successfully", status_code=status.HTTP_201_CREATED)
        return self.failure_response(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(BaseAPIView):
    """View for updating an existing user."""

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserSerializer,
    )
    def put(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return self.failure_response("User not found.", status_code=status.HTTP_404_NOT_FOUND)

        if request.user != user:
            return self.failure_response("You do not have permission to update this user.", status_code=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(serializer.data, status_code=status.HTTP_200_OK)
        return self.failure_response(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)



class RequestPasswordReset(BaseAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordRequestSerializer

    @swagger_auto_schema(
        request_body=ResetPasswordRequestSerializer,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email__iexact=email).first()

        if user:
            # Generate token
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            user.reset_token = token
            user.reset_token_created_at = now()
            user.save()

            # Return token in the response
            return self.success_response(
                message="Token generated successfully. Use this token to reset your password.",
                data={'token': token},
            )
        else:
            return self.failure_response(
                error="User with credentials not found",
                status_code=status.HTTP_404_NOT_FOUND
            )


class ResetPassword(BaseAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        token = request.data.get('token')
        new_password = data['new_password']
        confirm_password = data['confirm_password']

        if new_password != confirm_password:
            return self.failure_response(
                error="Passwords do not match",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(reset_token=token).first()

        if not user or user.is_reset_token_expired():
            return self.failure_response(
                error="Invalid or expired token",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Update the password
        user.set_password(new_password)
        user.clear_reset_token()

        return self.success_response(
            message="Password updated successfully",
            data=None
        )
