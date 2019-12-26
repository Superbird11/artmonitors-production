from django.contrib import admin

# Register your models here.

from .models import Collection, TemplateCollection, Work


class TemplateCollectionAdmin(admin.ModelAdmin):
    exclude = ('json_data',)

    def get_queryset(self, request):
        # https://stackoverflow.com/questions/34774028/how-to-ignore-loading-huge-fields-in-django-admin-list-display
        qs = super(TemplateCollectionAdmin, self).get_queryset(request)
        # tell Django to not retrieve json_data field from DB
        qs = qs.defer('json_data')
        return qs


admin.site.register(Collection)
admin.site.register(TemplateCollection, TemplateCollectionAdmin)
admin.site.register(Work)
