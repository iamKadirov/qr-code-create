from rest_framework import serializers
from .models import Site, ScanLog
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

class SiteSerializer(serializers.ModelSerializer):
    url_site = serializers.CharField()
    color = serializers.CharField(required=False)
    background_color = serializers.CharField(required=False)
    logo_image = serializers.ImageField(required=False)
    center_text = serializers.CharField(required=False)

    class Meta:
        model = Site
        fields = [
            'id', 
            'name', 
            'image', 
            'url_site', 
            'logo_type', 
            'logo_image', 
            'center_text', 
            'font_type', 
            'color', 
            'background_color',
            'style', 
            'scan_count', 
            'created_at', 
            'expire_duration', 
            'expire_at',]
        read_only_fields = ['id', 'image', 'scan_count', 'created_at', 'expire_at']

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
    def validate_background_color(self, value):
        if value:
            if not value.startswith("#") or len(value) != 7:
                raise serializers.ValidationError("Background color must be HEX like #ffffff")
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
    def validate_font_type(self, value):
        valid_fonts = ['arial', 'bold', 'script', 'mono', 'fancy']
        if value not in valid_fonts:
            raise serializers.ValidationError("Invalid font type")
        return value
        
class ScanLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanLog
        fields = '__all__'
        read_only_fields = ['site', 'scanned_at', 'ip_address', 'device_type', 'country', 'city']