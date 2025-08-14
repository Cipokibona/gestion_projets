from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdvanceViewSet, MainWalletViewSet, TaskWalletViewSet

router = DefaultRouter()
router.register(r'advances', AdvanceViewSet, basename='advance')
router.register(r'main-wallets', MainWalletViewSet, basename='main-wallet')
router.register(r'task-wallets', TaskWalletViewSet, basename='task-wallet')

urlpatterns = [
    path('', include(router.urls)),
]
