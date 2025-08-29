from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, TransactionErrorLogViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'error-logs', TransactionErrorLogViewSet, basename='transactionerrorlog')

urlpatterns = [
    path('', include(router.urls)),
]
