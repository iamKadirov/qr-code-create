from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

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
FONT_MAP = {
    "arial": "arial.ttf",
    "bold": "arialbd.ttf",
    "script": "pacifico.ttf",
    "mono": "cour.ttf",
    "fancy": "lobster.ttf",
}
DURATION_MAP = {
    '1m': timedelta(minutes=1),
    '10m': timedelta(minutes=10),
    '1h': timedelta(hours=1),
    '10h': timedelta(hours=10),
    '1d': timedelta(days=1),
    '7d': timedelta(days=7),
    '30d': timedelta(days=30),
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
    # STYLE_CHOICES = [
    #     ('square', 'Square'),
    #     ('dots', 'Dots'),
    #     ('rounded', 'Rounded'),
    #     ('smooth', 'Smooth'),
    # ]
    STYLE_CHOICES = [
        ("liquid", "Liquid"),
        ("dots", "Dots"),
        ("lines", "Lines"),
        ("square", "Square"),
    ]
    FONT_CHOICES = [
        ('arial', 'Arial'),
        ('bold', 'Bold'),
        ('script', 'Script'),
        ('mono', 'Mono'),
        ('fancy', 'Fancy'),
    ]
    Duration_choices = [
        ('1m', '1 Minute'),
        ('10m', '10 Minutes'),
        ('1h', '1 Hour'),
        ('10h', '10 Hours'),
        ('1d', '1 Day'),
        ('7d', '7 Days'),
        ('30d', '30 Days'),
        ('forever', 'Forever'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='media', blank=True, null=True)
    url_site = models.URLField(blank=True, null=True)
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='square')
    scan_count = models.IntegerField(default=0)
    color = models.CharField(max_length=7, default="#000000")
    logo_image = models.ImageField(upload_to='logos/', null=True, blank=True)
    logo_type = models.CharField(max_length=20, choices=LOGO_CHOICES, blank=True, default='')
    center_text = models.CharField(max_length=20, blank=True, null=True)
    font_type = models.CharField(max_length=20, choices=FONT_CHOICES, default='arial')
    created_at = models.DateTimeField(auto_now_add=True)
    expire_duration = models.CharField(max_length=20, choices=Duration_choices, default='forever')
    expire_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        now = timezone.now()

        if self.expire_duration in DURATION_MAP:
            self.expire_at = now + DURATION_MAP[self.expire_duration]
        else:
            self.expire_at = None

        super().save(update_fields=['expire_at'])


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

        fill_color = self.color if self.color else "#000000"

        import random

        def is_finder(x, y, size):
            return (
                (x < 7 and y < 7) or
                (x > size-8 and y < 7) or
                (x < 7 and y > size-8)
            )


        for y in range(size):
            for x in range(size):
                if not matrix[y][x]:
                    continue

                x1 = x * box
                y1 = y * box
                x2 = x1 + box
                y2 = y1 + box

                if is_finder(x, y, size):
                    draw.rectangle([x1, y1, x2, y2], fill=fill_color)
                    continue

                style = self.style or "liquid"

                if style == "liquid":

                    neighbors = sum([
                        matrix[y][x-1] if x > 0 else 0,
                        matrix[y][x+1] if x < size-1 else 0,
                        matrix[y-1][x] if y > 0 else 0,
                        matrix[y+1][x] if y < size-1 else 0,
                    ])

                    if neighbors >= 3:
                        radius = random.randint(6, 10)
                    elif neighbors == 2:
                        radius = random.randint(4, 8)
                    else:
                        radius = box // 2

                    offset = random.randint(-2, 2)

                    draw.rounded_rectangle(
                        [
                            x1 + offset,
                            y1 + offset,
                            x2 + offset,
                            y2 + offset
                        ],
                        radius=radius,
                        fill=fill_color
                    )

                elif style == "dots":

                    radius = random.randint(2, box // 2)

                    cx = x1 + box // 2
                    cy = y1 + box // 2

                    draw.ellipse(
                        [
                            cx - radius,
                            cy - radius,
                            cx + radius,
                            cy + radius
                        ],
                        fill=fill_color
                    )

                elif style == "lines":

                    if random.random() > 0.5:
                        draw.line([x1, y1, x2, y2], fill=fill_color, width=3)
                    else:
                        draw.line([x2, y1, x1, y2], fill=fill_color, width=3)

                else:
                    draw.rectangle([x1, y1, x2, y2], fill=fill_color)

        qr_img = img

        logo = None

        if self.logo_image:
            try:
                logo = Image.open(self.logo_image)
            except Exception:
                logo = None

        elif self.logo_type in LOGO_MAP:
            logo_path = os.path.join(settings.MEDIA_ROOT, 'logos', LOGO_MAP[self.logo_type])
            if os.path.exists(logo_path):
                logo = Image.open(logo_path)

        if logo:
            qr_w, qr_h = qr_img.size
            logo_size = qr_w // 4
            logo = logo.resize((logo_size, logo_size))

            pos = ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2)

            if logo.mode != 'RGBA':
                logo = logo.convert("RGBA")

            bg = Image.new("RGBA", logo.size, (255, 255, 255, 255))
            bg.paste(logo, (0, 0), logo)
            logo = bg

            qr_img.paste(logo, pos, mask=logo)

        elif self.center_text:
            draw_text = ImageDraw.Draw(qr_img)

            text = self.center_text.upper()

            from PIL import ImageFont

            try:
                font_file = FONT_MAP.get(self.font_type, "arial.ttf")
                font_path = os.path.join(settings.MEDIA_ROOT, "fonts", font_file)
                font = ImageFont.truetype(font_path, size=30)
            except:
                font = ImageFont.load_default()

            text = self.center_text.upper()

            qr_w, qr_h = qr_img.size
            center = (qr_w // 2, qr_h // 2)

            padding = 10

            bbox = draw_text.textbbox(center, text, font=font, anchor="mm")

            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

            bg_box = [
                center[0] - text_w//2 - padding,
                center[1] - text_h//2 - padding,
                center[0] + text_w//2 + padding,
                center[1] + text_h//2 + padding,
            ]

            draw_text.rectangle(bg_box, fill="white")
            draw_text.text(center, text, fill="black", font=font, anchor="mm")

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

    def __str__(self):
        return f"{self.site.name} - {self.scanned_at}"