from django.db import models


class OTPProvidor(models.Model):
    Providor = (
        ('SSLWireless', 'SSLWireless'),
        ('MIMSMS', 'MIMSMS'),
        ('Twilio', 'Twilio')
    )
    providor = models.CharField(max_length=12, choices=Providor)
    is_active = models.BooleanField(default=False, null=True, blank=True)
