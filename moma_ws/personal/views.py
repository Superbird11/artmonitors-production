import django.shortcuts
from django.http import HttpResponse
import moma_ws.settings as django_settings
from .models import PersonalFile
import datetime
import os

# Create your views here.


def index(request):
    personal_projects_list = PersonalFile.objects.filter(display=True)
    context = {
        'featured_projects': personal_projects_list,
        'copyright_year': str(datetime.datetime.now().year),
    }
    return django.shortcuts.render(request, 'personal/work_descriptions.html', context=context)


def show_webpage(request, name):
    file_obj = django.shortcuts.get_object_or_404(PersonalFile, name=name)
    context = {
        'resource_name': file_obj.name,
        'resource_url': django_settings.MEDIA_URL + str(file_obj.file)
    }
    print(context)
    return django.shortcuts.render(request, 'personal/redirect_to_file.html', context=context)
