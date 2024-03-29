"""sifapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import include, path
from planning import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"cameras", views.WebCamViewSet)
router.register(r"clients", views.ClientViewSet)
router.register(r"commandes", views.CommandeViewSet)
router.register(r"lines", views.BulkOrderLineViewSet)
router.register(r"operations", views.OperationViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/me", views.me),
]
