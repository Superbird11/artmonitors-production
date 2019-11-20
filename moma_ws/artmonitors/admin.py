from django.contrib import admin

# Register your models here.

from .models import Collection, TemplateCollection, Work

admin.site.register(Collection)
admin.site.register(TemplateCollection)
admin.site.register(Work)
