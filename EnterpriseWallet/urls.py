from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnterpriseWalletViewSet

router = DefaultRouter()
router.register(r'entreprise-wallets', EnterpriseWalletViewSet, basename='enterprise-wallet')

urlpatterns = [
    path('', include(router.urls)),
]
