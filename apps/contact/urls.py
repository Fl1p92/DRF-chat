from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

# API endpoints
urlpatterns = format_suffix_patterns([
    path('', views.api_root),
    path('users/', views.UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailAPIView.as_view(), name='user-detail'),
    path('users/<int:pk>/change-password/', views.UserPasswordChangeAPIView.as_view(), name='user-password-change'),
    path('contacts/', views.ListCreateUserContactsAPIView.as_view(), name='contact-list-detail'),
    path('contacts/<int:pk>/', views.DeleteUserContactAPIView.as_view(), name='contact-list-delete'),
])
