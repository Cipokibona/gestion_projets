from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialExpenseViewSet, MiscExpenseViewSet, GeneralExpenseViewSet, CompanyExpenseViewSet

router = DefaultRouter()
router.register(r'material-expenses', MaterialExpenseViewSet, basename='material-expenses')
router.register(r'misc-expenses', MiscExpenseViewSet, basename='misc-expenses')
router.register(r'general-expenses', GeneralExpenseViewSet, basename='general-expenses')
router.register(r'company-expenses', CompanyExpenseViewSet, basename='company-expenses')

urlpatterns = [
    path('', include(router.urls)),
]
