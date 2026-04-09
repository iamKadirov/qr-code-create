from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiteViewSet, redirect_to_site

router = DefaultRouter()
router.register(r'sites', SiteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]