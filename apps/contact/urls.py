from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

# API endpoints
urlpatterns = format_suffix_patterns([
    path('', views.api_root),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    path('users/<int:pk>/contacts/', views.UserContacts.as_view(), name='contactslist-detail'),
])
