from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialExpenseViewSet, MiscExpenseViewSet, GeneralExpenseViewSet

router = DefaultRouter()
router.register(r'material-expenses', MaterialExpenseViewSet, basename='material-expenses')
router.register(r'misc-expenses', MiscExpenseViewSet, basename='misc-expenses')
router.register(r'general-expenses', GeneralExpenseViewSet, basename='general-expenses')

urlpatterns = [
    path('', include(router.urls)),
]
