"""
A urls file for admin-restricted pages
"""


from django.contrib.admin import AdminSite
from django.conf.urls import patterns, url

class AddCollectionSite(AdminSite):

    def get_urls(self):
        urls = super(AddCollectionSite).get_urls(self)

        urls = [
                   url(r'^my_view/$', self.admin_view(index))
               ] + urls
    pass