from rest_framework.viewsets import ModelViewSet
from .models import Site
from .serializers import SiteSerializer
from django.shortcuts import get_object_or_404, redirect

class SiteViewSet(ModelViewSet):
  queryset = Site.objects.all()
  serializer_class = SiteSerializer

def redirect_to_site(request, pk):
  site = get_object_or_404(Site, pk=pk)
  site.scan_count += 1
  site.save()
  return redirect(site.url_site)