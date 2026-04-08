from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiteViewSet

router = DefaultRouter()
router.register(r'sites', SiteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]