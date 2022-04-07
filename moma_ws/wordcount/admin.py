from django.contrib import admin

# Register your models here.
import moma_ws.settings as django_settings
from .models import WordReference

admin.site.register(WordReference)
