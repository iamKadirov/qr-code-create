from rest_framework.viewsets import ModelViewSet
from .models import Site
from .serializers import SiteSerializer
from django.shortcuts import get_object_or_404, redirect

class SiteViewSet(ModelViewSet):
  queryset = Site.objects.all()
  serializer_class = SiteSerializer


def redirect_to_site(request, pk):
    site = get_object_or_404(Site, pk=pk)

    session_key = f"scanned_{pk}"

    if not request.session.get(session_key):
        site.scan_count += 1
        site.save()
        request.session[session_key] = True

    return redirect(site.url_site)