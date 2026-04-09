from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
import os
from django.conf import settings
from django.contrib.auth.models import User

LOGO_MAP = {
    "linkedin": "linkedin.png",
    "github": "github.png",
    "twitter": "twitter.png",
    "facebook": "facebook.png",
    "instagram": "instagram.png",
    "youtube": "youtube.png",
}

COLOR_MAP = {
    "linkedin": "#0A66C2",
    "github": "#000000",
    "twitter": "#1DA1F2",
    "facebook": "#1877F2",
    "instagram": "#E1306C",
    "youtube": "#FF0000",
}

class Site(models.Model):
    LOGO_CHOICES = [
       ('', 'No Logo'),
       ('linkedin', 'LinkedIn'),
       ('github', 'GitHub'),
       ('twitter', 'Twitter'),
       ('facebook', 'Facebook'),
       ('instagram', 'Instagram'),
       ('youtube', 'YouTube'),
    ]
    STYLE_CHOICES = [
    ('square', 'Square'),
    ('dots', 'Dots'),
    ('rounded', 'Rounded'),
    ('smooth', 'Smooth'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='media', blank=True, null=True)
    url_site = models.URLField(blank=True, null=True)
    logo_type = models.CharField(
                  max_length=20,
                  choices=LOGO_CHOICES,
                  blank=True,
                  default=''
                )
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='square')
    scan_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # data = f"http://127.0.0.1:8000/r/{self.id}/"
        data = f"http://qrcode.pythonanywhere.com/r/{self.id}/"

        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        matrix = qr.get_matrix()

        size = len(matrix)
        box = 10
        img_size = size * box

        img = Image.new("RGB", (img_size, img_size), "white")
        draw = ImageDraw.Draw(img)

        fill_color = COLOR_MAP.get(self.logo_type, "black")

        for y in range(size):
            for x in range(size):
                if matrix[y][x]:

                    x1 = x * box
                    y1 = y * box
                    x2 = x1 + box
                    y2 = y1 + box

                    if self.style == "smooth":
                        neighbors = [
                            matrix[y][x-1] if x > 0 else False,
                            matrix[y][x+1] if x < size-1 else False,
                            matrix[y-1][x] if y > 0 else False,
                            matrix[y+1][x] if y < size-1 else False,
                        ]

                        radius = 6 if any(neighbors) else box//2

                        draw.rounded_rectangle(
                            [x1, y1, x2, y2],
                            radius=radius,
                            fill=fill_color
                        )

                    elif self.style == "dots":
                        draw.ellipse([x1, y1, x2, y2], fill=fill_color)

                    elif self.style == "rounded":
                        draw.rounded_rectangle([x1, y1, x2, y2], radius=3, fill=fill_color)

                    else:
                        draw.rectangle([x1, y1, x2, y2], fill=fill_color)

        qr_img = img

        if self.logo_type and self.logo_type in LOGO_MAP:
            logo_file = LOGO_MAP[self.logo_type]

            logo_path = os.path.join(
                settings.MEDIA_ROOT,
                'logos',
                logo_file
            )

            if os.path.exists(logo_path):
                logo = Image.open(logo_path)

                qr_w, qr_h = qr_img.size
                logo_size = qr_w // 4
                logo = logo.resize((logo_size, logo_size))

                pos = ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2)

                if logo.mode != 'RGBA':
                    logo = logo.convert("RGBA")

                qr_img.paste(logo, pos, mask=logo)

        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f'image-{self.name.replace("/", "_")}.png'
        self.image.save(filename, File(buffer), save=False)

        super().save(update_fields=["image"])


class ScanLog(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='scans')

    scanned_at = models.DateTimeField(auto_now_add=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(null=True, blank=True)

    device_type = models.CharField(max_length=50, null=True, blank=True)
    browser = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=50, null=True, blank=True)

    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    is_unique = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.site.name} - {self.scanned_at}"