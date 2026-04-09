from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiteViewSet, redirect_to_site

router = DefaultRouter()
router.register(r'sites', SiteViewSet, basename='site')

urlpatterns = [
    path('', include(router.urls)),
]