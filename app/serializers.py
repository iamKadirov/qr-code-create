from rest_framework import serializers
from .models import Site, ScanLog
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

class SiteSerializer(serializers.ModelSerializer):
    url_site = serializers.CharField()

    class Meta:
        model = Site
        fields = ['id', 'name', 'image', 'url_site', 'logo_type', 'style', 'scan_count']
        read_only_fields = ['image', 'scan_count']

    def validate_url_site(self, value):
        value = value.strip().lower()

        if value and not value.startswith(('http://', 'https://')):
            value = 'https://' + value

        validator = URLValidator()
        try:
            validator(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid URL format!")

        return value
    
class ScanLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanLog
        fields = '__all__'
        read_only_fields = ['site', 'scanned_at', 'ip_address', 'device_type', 'country', 'city']