from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkforceGroupViewSet

router = DefaultRouter()
router.register(r'workforce-groups', WorkforceGroupViewSet, basename='workforce-group')

urlpatterns = [
    path('', include(router.urls)),
]
