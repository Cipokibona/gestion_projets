"""
URL configuration for budget_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from authem.views import FrontendAppView
import os
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', FrontendAppView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('authem.urls')),
    path('api/', include('expenses.urls')),
    path('api/', include('projects.urls')),
    path('api/', include('workforce.urls')),
    path('api/', include('finance.urls')),
    path('api/', include('tasks.urls')),
    path('api/', include('EnterpriseWallet.urls')),
    path('api/', include('Account.urls')),
    path('api/', include('Transaction.urls')),
    re_path(r'^(?!admin|api|static|assets).*$' , FrontendAppView.as_view(), name='frontend'),
]

urlpatterns += static("/assets/", document_root=os.path.join(settings.BASE_DIR, "static/assets/"))
