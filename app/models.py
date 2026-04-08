from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import os
from django.conf import settings

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
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='media', blank=True, null=True)
    url_site = models.URLField(blank=True, null=True)
    logo_type = models.CharField(
                  max_length=20,
                  choices=LOGO_CHOICES,
                  blank=True,
                  default=''
                )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        data = self.url_site or self.name

        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H
        )
        qr.add_data(data)
        qr.make(fit=True)

        # qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        fill_color = COLOR_MAP.get(self.logo_type, "black")

        qr_img = qr.make_image(
            fill_color=fill_color, 
            back_color="white"
        ).convert('RGB')
        

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

        filename = f'image-{self.name.replace("/", "_")}.png'
        self.image.save(filename, File(buffer), save=False)

        super().save(*args, **kwargs)