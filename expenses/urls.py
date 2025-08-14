from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialExpenseViewSet, MiscExpenseViewSet

router = DefaultRouter()
router.register(r'material-expenses', MaterialExpenseViewSet, basename='material-expenses')
router.register(r'misc-expenses', MiscExpenseViewSet, basename='misc-expenses')

urlpatterns = [
    path('', include(router.urls)),
]
