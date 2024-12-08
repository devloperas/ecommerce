from django.urls import path

from user.api.v1.views import RequestPasswordReset, ResetPassword, UserCreateView, UserUpdateView, UserListView

urlpatterns = [
    path('request-password-reset/', RequestPasswordReset.as_view(), name='request-password-reset'),
    path('reset-password/', ResetPassword.as_view(), name='reset-password'),
    path('create/', UserCreateView.as_view(), name='user-create'),
    path('update/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
    path('users/', UserListView.as_view(), name='user-list'),
]