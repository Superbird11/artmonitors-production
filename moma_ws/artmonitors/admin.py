from django.contrib import admin

# Register your models here.

from .models import Collection, TemplateCollection, Work


class TemplateCollectionAdmin(admin.ModelAdmin):
    exclude = ('json_data',)


admin.site.register(Collection)
admin.site.register(TemplateCollection, TemplateCollectionAdmin)
admin.site.register(Work)
