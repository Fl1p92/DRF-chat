from rest_framework import routers

from . import views


router = routers.SimpleRouter()
router.register('chats', views.ListDestroyChatAPIViewSet, basename='chat')

urlpatterns = router.urls