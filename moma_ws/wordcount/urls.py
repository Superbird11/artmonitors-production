from django.urls import path

from . import views

app_name = 'personal'
urlpatterns = [
    path('tick/<slug:word>', views.increment_counter, name='tick'),
    path('check/<slug:word>', views.check_counter, name='check'),
    path('reset/<slug:word>', views.reset_counter, name='reset'),
]
