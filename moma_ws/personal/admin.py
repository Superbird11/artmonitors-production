from django.contrib import admin
from django import forms
import os
# Register your models here.

import moma_ws.settings as django_settings
from .models import PersonalFile


class UploadFileForm(forms.ModelForm):
    name = forms.CharField(max_length=200)
    description = forms.Textarea()
    display = forms.BooleanField
    folder = forms.CharField(max_length=200)
    file = forms.FileField()
    auxiliary_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = PersonalFile
        fields = '__all__'


class FileAdmin(admin.ModelAdmin):
    form = UploadFileForm
    model = PersonalFile

    fields = ['name', 'description', 'display', 'folder', 'file', 'auxiliary_files']

    def save_model(self, request, obj, form, change):
        aux_files = request.FILES.getlist('auxiliary_files')
        for f in aux_files:
            path = os.path.join(django_settings.MEDIA_ROOT + 'personal', obj.folder, f.name) \
                    if obj.folder and len(obj.folder) > 0 \
                    else os.path.join(django_settings.MEDIA_ROOT + 'personal', f.name)
            if not os.path.isdir(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            with open(path, 'wb') as new_file:
                for chunk in f.chunks():
                    new_file.write(chunk)
        super().save_model(request, obj, form, change)


admin.site.register(PersonalFile, FileAdmin)
