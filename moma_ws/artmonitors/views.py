# from django.shortcuts import render

import django.shortcuts
import django.http
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt

import datetime
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random
import string
import traceback
import math
import os
import sys

import moma_ws.settings as django_settings
from .models import Collection, Work, group_works
from .add_collection_utils import create_collection

# Create your views here.


def index(request):
    """
    Presents the index page of this website, displaying the most recent new collection
    and several featured works from the history of the website.
    """
    # get newest collection from database
    newest_collection = Collection.objects.latest('id')
    # get featured works
    featured_works = random.sample(list(Work.objects.filter(featured=True)), 5)
    # get datetime of last monday
    last_monday = django_settings.LAST_UPDATE_DATE
    # prepare context
    context = {
        'newest_coll': newest_collection,
        'featured_works': featured_works,
        'last_monday_date': last_monday.strftime('%d %B %Y'),
        'copyright_year': datetime.datetime.now().year
    }
    return django.shortcuts.render(request, 'artmonitors/index.html', context)


def view_all_collections(request):
    """
    Presents a view of all collections' abbreviations and names, in a list
    """
    # get all collection database objects
    collections = sorted(Collection.objects.all())
    # build context
    context = {
        'collections': collections,
        'copyright_year': str(datetime.datetime.now().year)
    }
    return django.shortcuts.render(request, 'artmonitors/all_collections.html', context)


def view_collection(request, coll_abbrev):
    """
    Presents a view of a particular collection, including its description and
    thumbnails of each work it contains
    """
    # get regular database objects
    collection = django.shortcuts.get_object_or_404(Collection, abbrev=coll_abbrev)
    debug_collection = django.shortcuts.get_object_or_404(Collection, abbrev='macc2')
    print(collection)
    print(debug_collection)

    # get prev and next collections
    try:
        prev_collection = Collection.objects.get(id=collection.id - 0.5)
    except Collection.DoesNotExist:
        try:
            prev_collection = Collection.objects.get(id=collection.id - 1)
        except Collection.DoesNotExist:
            prev_collection = None
    try:
        next_collection = Collection.objects.get(id=collection.id + 0.5)
    except Collection.DoesNotExist:
        try:
            next_collection = Collection.objects.get(id=collection.id + 1)
        except Collection.DoesNotExist:
            next_collection = None
    # get works, and group them appropriately
    works = sorted(Work.objects.filter(collection=collection))
    debug_works = sorted(Work.objects.filter(collection=debug_collection))

    print(works)
    print(debug_works)


    work_groups = group_works(works, 3)
    # build context
    context = {
        'coll': collection,
        'prev_coll': prev_collection,
        'next_coll': next_collection,
        'work_groups': work_groups,
        'copyright_year': datetime.datetime.now().year
    }
    # return page template accordingly
    return django.shortcuts.render(request, 'artmonitors/view_collection.html', context)


def view_work(request, coll_abbrev, work_name):
    """
    Presents a view of a particular work, including its title, image, and
    description, if it has one
    """
    # get regular database objects for these
    collection = django.shortcuts.get_object_or_404(Collection, abbrev=coll_abbrev)
    work = django.shortcuts.get_object_or_404(Work, collection=collection, pagename=work_name)
    # get previous and next works
    try:
        prev_work = Work.objects.get(id=work.id - 1)
    except Work.DoesNotExist:
        prev_work = None
    try:
        next_work = Work.objects.get(id=work.id + 1)
    except Work.DoesNotExist:
        next_work = None
    # build context
    context = {
        'collection': collection,
        'work': work,
        'prev_work': prev_work,
        'next_work': next_work,
        'copyright_year': str(datetime.datetime.now().year)
    }
    # return page template accordingly
    return django.shortcuts.render(request, 'artmonitors/view_work.html', context)


def view_archive(request):
    """
    Presents a view of the names of all works currently existing in the collection,
    in order of most recent
    """
    # get database objects for works
    works = sorted(Work.objects.all())
    works.reverse()
    work_groups = group_works(works, 5)
    # build context
    context = {
        'work_groups': work_groups,
        'copyright_year': datetime.datetime.now().year
    }
    return django.shortcuts.render(request, 'artmonitors/archive_text.html', context)


def view_full_archive(request):
    """
    Presents a view of thumbnails and names of all works currently existing in the
    collection, in order of most recent
    """
    # get database objects for works
    works = sorted(Work.objects.all())
    works.reverse()
    work_groups = group_works(works, 3)
    # build context
    context = {
        'work_groups': work_groups,
        'copyright_year': datetime.datetime.now().year
    }
    return django.shortcuts.render(request, 'artmonitors/archive_full.html', context)

def view_archive_page(request, page_num):
    """
    Presents a view of the 'page_num'th 60 works in the archive.
    """
    # validate page_num is an integer and turn it into one
    try:
        current_page = int(page_num)
    except ValueError:
        return django.http.HttpResponseBadRequest()
    page_num = current_page - 1

    # get database objects for works
    works = sorted(Work.objects.all())
    works.reverse()

    # filter works
    works_per_page = 60
    if page_num * works_per_page > len(works) or page_num < 0:
        return django.http.Http404()
    elif (page_num + 1) * works_per_page > len(works):
        filtered_works = works[page_num * works_per_page:]
    else:
        filtered_works = works[page_num * works_per_page:(page_num + 1) * works_per_page]

    # group filtered works together
    work_groups = group_works(filtered_works, 3)
    max_page_num = math.ceil(len(works) / works_per_page)

    # build context
    context = {
        'works_per_page': works_per_page,
        'current_page': current_page,
        'page_list': range(1, max_page_num + 1),  # [1, 2, 3, 4, ..., max_page_num].
        'work_groups': work_groups,
        'copyright_year': datetime.datetime.now().year
    }
    return django.shortcuts.render(request, 'artmonitors/archive_page.html', context)


def about_us(request):
    """
    Returns a simple "About Us" page
    """
    context = {
        'copyright_year': str(datetime.datetime.now().year)
    }
    return django.shortcuts.render(request, 'artmonitors/about_us.html', context)


def contact_us(request):
    """
    Returns a simple "Contact Us" page
    """
    context = {
        'copyright_year': str(datetime.datetime.now().year)
    }
    return django.shortcuts.render(request, 'artmonitors/contact_us.html', context)


@csrf_exempt
def add_collection(request):
    """
    A method for adding a collection, protected as possible with SSH keys.
    The request must first pass basic authentication, after which it must
    exactly contain a particular key, which has been encrypted on the client
    side with this server's public key and which will be decrypted and verified
    with this server's private key. If the request passes all these steps, it
    will be forwarded to the actual add_collection routines.
    """
    # declare decryption message for decryption
    def decrypt_message(encoded_encrypted_msg, private_key):
        # source: https://gist.github.com/syedrakib/241b68f5aeaefd7ef8e2
        # decrypted = decryptor.decrypt(ast.literal_eval(str(encrypted)))
        decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
        decryptor = PKCS1_OAEP.new(private_key)
        decoded_decrypted_msg = decryptor.decrypt(decoded_encrypted_msg)
        # decoded_decrypted_msg = private_key.decrypt(decoded_encrypted_msg)
        return decoded_decrypted_msg

    def encrypt_message(a_message, public_key):
        # source: https://gist.github.com/syedrakib/241b68f5aeaefd7ef8e2
        encryptor = PKCS1_OAEP.new(public_key)
        encrypted_msg = encryptor.encrypt(a_message)
        # encrypted_msg = public_key.encrypt(a_message, 32)[0]
        encoded_encrypted_msg = base64.b64encode(encrypted_msg)  # base64 encoded strings are database friendly
        return encoded_encrypted_msg

    # verify is post request
    if request.method != "POST":
        print("add_collection failed: request was not POST")
        return django.http.HttpResponseNotFound()
    print("Verified POST request for add_collection")

    # verify basic authentication
    metadata = request.META
    http_auth_type, http_auth_base64 = metadata['HTTP_AUTHORIZATION'].split(' ')
    if not http_auth_type == "Basic":
        print("add_collection failed: request was not basic auth")
        st_body = {'stacktrace': 'Invalid authentication method was provided (Basic Auth only)'}
        return django.http.HttpResponse(status=401, content=json.dumps(st_body))
    with open('artmonitors/keys/add_collection_permissions', 'r') as perm_file:
        pflines = perm_file.readlines()
        expected_auth_base64 = base64.encodebytes(
            bytes('{}:{}'.format(pflines[0].strip(), pflines[1].strip()), 'utf8')).strip()
    if not bytes(http_auth_base64, 'utf8') == expected_auth_base64:
        print("add_collection failed: incorrect credentials")
        st_body = {'stacktrace': 'Invalid Credentials'}
        return django.http.HttpResponse(status=401, content=json.dumps(st_body))

    print("Verified basic auth")

    # verify random key was sent correctly
    data = JSONParser().parse(request)
    if 'key' not in data:
        print("add_collection failed: no 'key' field present")
        st_body = {'stacktrace': 'No key was provided'}
        return django.http.HttpResponse(status=401, content=json.dumps(st_body))
    with open('artmonitors/keys/add_collection_rsa_key', 'rb') as priv_key_file:
        private_key = RSA.importKey(priv_key_file.read())
    decoded_key = decrypt_message(data['key'], private_key)
    with open('artmonitors/keys/random_key', 'rb') as random_key_file:
        random_key = random_key_file.read()
        if decoded_key != random_key:
            print("add_collection failed: 'key' was incorrect")
            st_body = {'stacktrace': 'Incorrect Key'}
            return django.http.HttpResponse(status=401, content=json.dumps(st_body))
    print("Verified random key auth")

    # checks out imo. Will need to change the random key though. That will be done in the response.
    try:
        invalid_reason = create_collection(data)
    except Exception as e:
        st_body = {
            'stacktrace': traceback.format_exc()
        }
        sys.stderr.write(traceback.format_exc())
        return django.http.HttpResponse(status=500, content=json.dumps(st_body))

    if invalid_reason:
        print("Failed: {}".format(invalid_reason))
        st_body = {'stacktrace': invalid_reason}
        return django.http.HttpResponse(status=400, content=json.dumps(st_body))

    # after successful upload, change date internally
    django_settings.LAST_UPDATE_DATE = datetime.date.today()

    # generate new random_key
    random_base64 = base64.encodebytes(bytes(''.join(random.choice(string.printable) for _ in range(256)), 'utf8'))
    with open('artmonitors/keys/random_key', 'wb') as random_key_file:
        random_key_file.write(random_base64)

    with open('artmonitors/keys/add_collection_client_key.pub', 'rb') as client_key_file:
        client_key = RSA.importKey(client_key_file.read())

    resp_dict = {'key': encrypt_message(random_base64, client_key).decode('utf8')}
    return django.http.HttpResponse(content=json.dumps(resp_dict), content_type='application/json', status=200)


def slideshow(request):
    all_works = [[str(work.name), os.path.join('/static/media', str(work.path)), str(work.pagename),
                  str(work.collection.abbrev)] for work in Work.objects.all()]
    context = {
        'work_list': json.dumps(all_works)
    }
    return django.shortcuts.render(request, 'artmonitors/slideshow.html', context)


def slideshow_group(request, group_name):
    context = {
        'group_name': group_name
    }
    return django.shortcuts.render(request, 'artmonitors/slideshow_groups.html', context)


def group(request):
    collections = {c: group_works([w for w in Work.objects.filter(collection=c)], 3) for c in Collection.objects.all()}
    collection_info = {str(c.id): {
        'abbrev': str(c.abbrev),
        'name': str(c.name),
        'works': {
            str(w.id): {
                'name': str(w.name),
                'path': str(w.path),
                'filename': str(w.filename),
                'pagename': str(w.pagename),
                'thumbnail': str(w.thumbnail),
                'selected': str(True),
            } for w in Work.objects.filter(collection=c)
        },
    } for c in collections}
    selected_collection = Collection.objects.get(id=1)
    selected_works = collections[selected_collection]
    # works = {c.id: group_works([w for w in Work.objects.filter(collection=c)], 3) for c in collections}

    print(str(collection_info))

    context = {
        'copyright_year': str(datetime.datetime.now().year),
        'collections': collections,
        'collection_info': json.dumps(collection_info),
        'selected_collection': selected_collection,
        'selected_works': selected_works
        # 'works': works
    }
    print(collections)
    return django.shortcuts.render(request, 'artmonitors/group.html', context)
