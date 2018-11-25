"""
A django-required file for determining the set of URLs for this site
"""

from django.urls import include, path

from . import views

app_name = 'artmonitors'
urlpatterns = [
    # top-level directory, show index
    path('',                                                views.index,                name='index'),
    # view list of collections
    path('collections/',                                    views.view_all_collections, name='view_all_collections'),
    # view specific collection
    path('collections/<slug:coll_abbrev>',                  views.view_collection,      name='view_collection'),
    # view specific work page
    path('collections/<slug:coll_abbrev>/<slug:work_name>', views.view_work,            name='view_work'),
    # view archive
    path('archive',                                         views.view_archive,         name='view_archive'),
    path('archive/full',                                    views.view_full_archive,    name='view_full_archive'),
    path(r'archive/<slug:page_num>',                        views.view_archive_page,    name='view_archive_page'),
    # view about page
    path('about',                                           views.about_us,             name='view_about'),
    # view contact page
    path('contact',                                         views.contact_us,           name='view_contact'),
    # slideshow index
    path('slideshow',                                       views.slideshow,            name='slideshow'),

    # admin add-collection page
    path('add_collection',                                  views.add_collection),
    path('projects/',                                        include('personal.urls')),

    # old paths/redirectors
    path('about.html',                                      views.about_us,             name='old_about'),
    path('contact.html',                                    views.contact_us,           name='old_contact'),
    path('archive.html',                                    views.view_archive,         name='old_archive'),
    path('pages',                                           views.view_all_collections, name='old_pages'),
    path('pages/index.html',                                views.view_all_collections, name='old_pages_idx'),
    path('pages/<slug:coll_abbrev>',                        views.view_collection,      name='old_view_collection'),
    path('pages/<slug:coll_abbrev>/index.html',             views.view_collection,      name='old_view_collection_idx'),
    path('pages/<slug:coll_abbrev>/<slug:work_name>.html',  views.view_work,            name='old_view_work')
]
