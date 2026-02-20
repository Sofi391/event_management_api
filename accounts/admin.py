from django.contrib import admin
from .models import OtpCode

# Register your models here.
@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ['code','user__username', 'used','created_at','purpose']

