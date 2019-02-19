from django.contrib import admin
from django.conf import settings
from django.urls import path, include

from rest_framework import routers

from apps.contact import views as contact_views
from apps.chats import views as chats_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
]

router = routers.DefaultRouter()
router.register('users', contact_views.UserAPIViewSet, basename='user')
router.register('contacts', contact_views.CreateDestroyListContactsAPIViewSet, basename='contact')
router.register('chats', chats_views.ListDestroyChatAPIViewSet, basename='chat')

urlpatterns += router.urls

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls)),]
