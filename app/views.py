from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Site, ScanLog
from .serializers import SiteSerializer, ScanLogSerializer
from django.shortcuts import get_object_or_404, redirect
from user_agents import parse
import requests
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import F

class SiteViewSet(ModelViewSet):
  # queryset = Site.objects.all()
  serializer_class = SiteSerializer
  def get_queryset(self):
     if self.request.user.is_authenticated:
        return Site.objects.filter(user=self.request.user)
     else:
        if not self.request.session.session_key:
            self.request.session.create()
        return Site.objects.filter(session_key=self.request.session.session_key)
  
  def perform_create(self, serializer):
     if self.request.user.is_authenticated:
        serializer.save(user=self.request.user)
     else:
        if not self.request.session.session_key:
            self.request.session.create()
        serializer.save(session_key=self.request.session.session_key)

  @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
  def analytics(self, request, pk=None):
    site = self.get_object()
    logs = site.scans.all().order_by('-scanned_at')
    serializer = ScanLogSerializer(logs, many=True)
    return Response(serializer.data)



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def get_location(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=2).json()
        return res.get('country'), res.get('city')
    except:
        return None, None

def redirect_to_site(request, pk):
    site = get_object_or_404(Site, pk=pk)

    if site.expire_at and timezone.now() > site.expire_at:
        return HttpResponse("This QR code has expired", status=410)

    user_agent_str = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_str)

    os = user_agent.os.family if user_agent.os else "Unknown"

    if user_agent.is_mobile:
        device_type = "Mobile"
    elif user_agent.is_tablet:
        device_type = "Tablet"
    else:
        device_type = "Desktop"

    browser = user_agent.browser.family if user_agent.browser else "Unknown"

    ip = get_client_ip(request)
    country, city = get_location(ip)

    ScanLog.objects.create(
        site=site,
        ip_address=ip,
        user_agent=user_agent_str,
        device_type=device_type,
        browser=browser,
        os=os,
        country=country,
        city=city
    )

    Site.objects.filter(pk=site.pk).update(scan_count=F('scan_count') + 1)

    return redirect(site.url_site)