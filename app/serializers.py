from rest_framework import serializers
from .models import Site

class SiteSerializer(serializers.ModelSerializer):
  class Meta:
    model = Site
    fields = ['id', 'name', 'image', 'url_site', 'logo_type']
    read_only_fields = ['image']