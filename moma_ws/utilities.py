"""

A module containing single-use utility methods for setting up the environment.
All of these methods are meant for use in the local environment - paths are
hardcoded in the associated configuration file, and the operations are
extremely specific to the existing layout of the filesystem it was written for

This file is meant to be run standalone from its current directory, with the
simple command `python utility.py`.

"""
__author__ = "Louis Jacobowitz <ldjacobowitzer@gmail.com>"

import os
import re
import csv
import shutil
import json


""" Global variable to keep track of paths """
paths_dict = None


def getpath(key):
    """
    Uses a configuration file to get an absolute url on the host machine, which is used
    for filesystem operations like copying data to a local datastore
    :param key: url get
    :return: the path for the given key
    """
    global paths_dict
    if not paths_dict:
        with open('artmonitors/keys/utility_dirs.json', 'r') as keyfile:
            paths_dict = json.loads(keyfile.read())
    return paths_dict[key]


def get_collection_indices():
    """
    Reads the eponymous list.txt file, parses its data into a more well-defined CSV format,
    and stores that file locally.
    """
    with open(getpath('get_collection_indices'), 'r') as list_file:
        list_lines = list_file.readlines()
        collections = []
        for line in list_lines:
            collection_info = re.findall(r'(\w+|\w+.\w+) - (\w+) - (.+)', line.strip())[0]
            # (index, abbreviation, name)
            collections.append(collection_info)
    with open('static/collections.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        for collection in collections:
            writer.writerow(collection)


def get_work_names():
    """
    Uses the ordering of get_collection_indices() to create a list of works, in order
    """
    with open('static/collections.csv', 'r') as collections_file:
        reader = csv.reader(collections_file)
        collections = [row[1] for row in reader]
    work_list = []
    count = 1
    for abbrev in collections:
        try:
            collection_list = os.listdir(getpath('get_work_names') % abbrev)
        except FileNotFoundError:
            break
        collection_list.sort()
        for work in collection_list:
            if '.ds_store' in work.lower() or '.txt' in work.lower():
                continue
            work_list.append([count, abbrev, work[:work.index('.')], work])
            # [index, collection_abbrev, work name, work filename]
            count += 1
    with open('static/works.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        for work in work_list:
            writer.writerow(work)


def delete_all_works():
    """
    Deletes all Collection and Work objects in the database.
    """
    from django.core.wsgi import get_wsgi_application
    os.environ['DJANGO_SETTINGS_MODULE'] = 'moma_ws.settings'
    get_wsgi_application()

    from artmonitors.models import Collection, Work
    Collection.objects.all().delete()
    Work.objects.all().delete()


def repopulate_database():
    """
    Using the contents of the given static files collections.csv and works.csv,
    (re)populates the sqlite database with the complete contents of artmonitors.
    """
    from django.core.wsgi import get_wsgi_application
    from django.template import Context, Template
    os.environ['DJANGO_SETTINGS_MODULE'] = 'moma_ws.settings'
    get_wsgi_application()

    from artmonitors.models import Collection, Work

    # initialize collections
    collection_objects = []
    with open('static/collections.csv', 'r') as collection_file:
        collection_reader = csv.reader(collection_file)
        for collection_row in collection_reader:
            # get regular fields
            id, abbrev, name = collection_row
            id = float(id)
            # extract description where possible
            index_url = getpath('repopulate_index') % abbrev
            try:
                with open(index_url, 'r') as collection_index:
                    collection_lines = collection_index.readlines()
                    possible_description = collection_lines[25].strip().replace('<p>', '').replace('</p>', '')
            except FileNotFoundError:
                continue
            # parse description if it's real
            if 'div>' in possible_description or '<div' in possible_description or '<table>' in possible_description:
                final_description = None
            else:
                # use regex replacement to make a mini-template
                description = possible_description
                description = re.sub(r'<a href="\.\./(.+?)/index\.html">(.+?)</a>',
                                     r'''<a href="{% url 'artmonitors:view_collection' coll_abbrev='\1' %}">\2</a>''',
                                     description)
                description = re.sub(r'<a href="\.\./(.+?)/(.+?)\.(\w+)">(.+?)</a>',
                                     r'''<a href="{% url 'artmonitors:view_work' coll_abbrev='\1' work_name='\2' %}">\4</a>''',
                                     description)
                description = re.sub(r'<a href="([^{}]+?)\.(\w+)">(.+?)</a>',
                                     """<a href="{% url \'artmonitors:view_work\' coll_abbrev='""" + abbrev + r'''' work_name='\1' %}">\3</a>''',
                                     description)
                for s in re.findall(r"work_name='([^']+)'", description):
                    description = description.replace(s, re.sub(r'[^\x00-\x7f]', r'', s).replace(',', '').replace("'", ''))
                # parse the mini-template into a final description
                desc_template = Template(description)
                final_description = desc_template.render(Context({}))
            # assign summary filename, and actually copy summary image
            summary = 'artmonitors/summaries/%s.gif' % abbrev
            if not os.path.exists('static/media/artmonitors/summaries'):
                os.makedirs('static/media/artmonitors/summaries')
            shutil.copy(getpath('repopulate_copygif') % abbrev,
                        'static/media/artmonitors/summaries/%s.gif' % abbrev)
            # create object
            collection_obj = Collection(
                id=id,
                abbrev=abbrev,
                name=name,
                description=final_description,
                summary=summary
            )
            collection_objects.append(collection_obj)
    # initialize works
    works_objects = []
    with open('static/works.csv', 'r') as works_file:
        works_reader = csv.reader(works_file)
        for works_row in works_reader:
            # get regular fields
            id, collection_abbrev, name, fname = works_row
            id = int(id)
            # make exception for Deep Pond
            if name == "Deep Pond":
                works_objects[0].id = id
                id = 1

            # determine pagename
            pagename = re.sub(r'[^\x00-\x7f]', r'', name.lower().replace(' ', '-').replace(',', '').replace("'", ''))
            # get proper collection, using list comprehension shortcut
            collection = [i for i in collection_objects if i.abbrev == collection_abbrev][0]
            # get proper description, if the work has one, and parse it
            page_url = getpath('repopulate_pages') % (collection_abbrev, name.lower().replace(' ', '-'))
            with open(page_url, 'r') as page_file:
                page_lines = page_file.readlines()
                possible_description = page_lines[41].strip().replace('<p>', '').replace('</p>', '').replace('<br>', '')
            if '<div' in possible_description or '</div' in possible_description:
                final_description = None
            else:
                # use regex replacement to make a mini-template
                description = possible_description
                description = re.sub(r'<a href="\.\./(.+?)/index\.html">(.+?)</a>',
                                     r'''<a href="{% url 'artmonitors:view_collection' coll_abbrev='\1' %}">\2</a>''',
                                     description)
                description = re.sub(r'<a href="\.\./(.+?)/(.+?)\.(\w+)">(.+?)</a>',
                                     r'''<a href="{% url 'artmonitors:view_work' coll_abbrev='\1' work_name='\2' %}">\4</a>''',
                                     description)
                description = re.sub(r'<a href="([^{}]+?)\.(\w+)">(.+?)</a>',
                                     """<a href="{% url \'artmonitors:view_work\' coll_abbrev='""" + collection_abbrev + r'''' work_name='\1' %}">\3</a>''',
                                     description)
                for s in re.findall(r"work_name='([^']+)'", description):
                    description = description.replace(s, re.sub(r'[^\x00-\x7f]', r'', s).replace(',', '').replace("'", ''))
                # parse the mini-template into a final description
                desc_template = Template(description)
                final_description = desc_template.render(Context({}))
            # assign filename and thumbnail filename, also actually copy files
            path = 'artmonitors/works/%s/%s' % (collection_abbrev, fname)
            thumbnail = 'artmonitors/thumbnails/%s/%s' % (collection_abbrev, fname)
            if not os.path.exists('static/media/artmonitors/works/%s' % collection_abbrev):
                os.makedirs('static/media/artmonitors/works/%s' % collection_abbrev)
            shutil.copy(getpath('repopulate_copyimg') % (collection_abbrev, fname),
                        'static/media/artmonitors/works/%s/%s' % (collection_abbrev, fname))
            if not os.path.exists('static/media/artmonitors/thumbnails/%s' % collection_abbrev):
                os.makedirs('static/media/artmonitors/thumbnails/%s' % collection_abbrev)
            shutil.copy(getpath('repopulate_copythumb') % (collection_abbrev,
                                                                                                  fname),
                        'static/media/artmonitors/thumbnails/%s/%s' % (collection_abbrev, fname))
            # create object
            work_obj = Work(
                id=id,
                collection=collection,
                name=name,
                filename=fname,
                pagename=pagename,
                description=final_description,
                path=path,
                thumbnail=thumbnail
            )
            works_objects.append(work_obj)
    # save to database
    for coll_obj in collection_objects:
        coll_obj.save()
    for works_obj in works_objects:
        works_obj.save()


def set_featured_works():
    """
    Using a configuration file, designates certain newly-loaded works as "featured", allowing
    them to show up randomly on the front page of the website.
    """
    from artmonitors.models import Collection, Work
    with open('static/artmonitors/featured_works.csv', 'r') as featured_file:
        featured_reader = csv.reader(featured_file)
        for featured_row in featured_reader:
            abbrev, pagename = featured_row
            collection = Collection.objects.get(abbrev=abbrev)
            work = Work.objects.get(collection=collection, pagename=pagename)
            work.featured = True
            work.save()


if __name__ == '__main__':
    get_collection_indices()
    get_work_names()
    delete_all_works()
    repopulate_database()
    set_featured_works()
