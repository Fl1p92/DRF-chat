from rest_framework import routers

from . import views


router = routers.SimpleRouter()
router.register('users', views.UserAPIViewSet, basename='user')
router.register('contacts', views.CreateDestroyListContactsAPIViewSet, basename='contact')

urlpatterns = router.urls
