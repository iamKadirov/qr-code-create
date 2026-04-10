from rest_framework import serializers
from .models import Site, ScanLog
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

class SiteSerializer(serializers.ModelSerializer):
    url_site = serializers.CharField()
    color = serializers.CharField(required=False)
    logo_image = serializers.ImageField(required=False)

    class Meta:
        model = Site
        fields = ['id', 'name', 'image', 'url_site', 'logo_type', 'logo_image', 'color', 'style', 'scan_count']
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
    def validate_color(self, value):
        if value:
            if not value.startswith("#") or len(value) != 7:
                raise serializers.ValidationError("Color must be HEX like #ffffff")
        return value
    def validate_logo_image(self, value):
        if value:
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError("Logo too large (max 2MB)")
        return value
    def validate(self, data):
        if data.get("logo_image") and data.get("logo_type"):
            data["logo_type"] = ""
        return data
        
class ScanLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanLog
        fields = '__all__'
        read_only_fields = ['site', 'scanned_at', 'ip_address', 'device_type', 'country', 'city']