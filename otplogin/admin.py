from django.contrib import admin
from .models import *


class OTPAdmin(admin.ModelAdmin):
    list_display = ['providor', 'is_active']


admin.site.register(OTPProvidor, OTPAdmin)
