"""
A file containing various utilities (mostly involving image manipulation)
involved in the Add Collection/Work process
"""

from PIL import Image
from .models import Collection, Work
from django.conf import settings
from django.template import Context, Template, TemplateSyntaxError
import os
import numpy
import imageio
import re
import base64


def create_summary_gif(image_list, filename, width=300, duration=2):
    """
    Given a list of PIL Image objects, creates and saves a .gif file consisting
    of the images. The resulting .gif will always have the given width, but its
    height will be determined according to the average aspect ratio between all
    component images. Images will be resized against their aspect ratio to match
    the final dimensions of the .gif.
    :param image_list: A python list of PIL Image objects
    :param filename: The filename to which to write the .gif
    :param width: The final width of the generated .gif
    :param duration: The duration of each frame of the generated .gif
    """
    # Obtain the average aspect ratio between component images
    #   This aspect ratio is height/width as opposed to the usual width/height,
    #   to simplify later calculations
    avg_aspect_ratio = 0.0
    count = 0
    for img in image_list:
        avg_aspect_ratio += float(img.size[1]) / float(img.size[0])
        count += 1
    avg_aspect_ratio /= float(count)

    # Resize all images to match the final size and aspect ratio
    final_dimensions = (width, int(width * avg_aspect_ratio))
    final_image_list = [img.resize(final_dimensions, Image.ANTIALIAS) for img in image_list]

    # create final gif using imageio
    numpy_images = [numpy.asarray(i) for i in final_image_list]
    imageio.mimwrite(uri=filename,
                     ims=numpy_images,
                     loop=0,
                     duration=2,
                     palettesize=256,
                     subrectangles=True)

    # # create gif. Silence console while we do so, because this process is very noisy
    # save_stdout = sys.stdout
    # sys.stdout = open(os.devnull, 'w')
    # writeGif(
    #     filename=filename,
    #     images=final_image_list,
    #     duration=duration,
    #     loops=float('inf'), # repeat=True
    #     dither=True)
    # sys.stdout = save_stdout


def create_thumbnail(img, max_width=400.0, max_height=300.0):
    """
    Takes the given PIL Image and creates a thumbnail version for it.
    Preserves the aspect ratio of the original image, but constrains the
    resized image to fit within the given boundaries.

    :param img: A Pillow Image object
    :param max_width: The maximum width of the final thumbnail
    :param max_height: The maximum height of the final thumbnail
    :return: a Pillow Image object that is smaller and more compact.
    """
    img_width = float(img.size[0])
    img_height = float(img.size[1])
    ratio = max(img_width / max_width, img_height / max_height)
    new_width = int(img_width / ratio)
    new_height = int(img_height / ratio)
    resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)
    return resized_img


def create_collection(data):
    """
    Given an appropriately-formatted REST request, creates a new collection accordingly.
    The appropriate JSON format of the request is:

    {
        "key": "{base64-encoded rsa-encrypted random key}",
        "name": "Example Collection Modern Art",
        "abbrev": "ECMA",
        "description": "Some lengthy description, in HTML but using {{}} notation for links",
        "works": [
            {
                "name": "Example Work 1"
                "filename": "Example Work 1.jpg",
                "description": "Some short description of the work, or null",
                "img": "{base64 encoding of the binary file}"
            },
            {
                "name": "Example Work 2"
                "filename": "Example Work 2.jpg",
                "description": "Some short description of the work, or null",
                "img": "{base64 encoding of the binary file}"
            },
            ...
        ]
    }         

    :param data: a JSON dict formatted as above
    :return: None if successful, or a string containing an error message if something went wrong.
    """
    def validate_add_request(d):
        """
        Validates all fields in the given request d. Returns a list of strings, with
        one error per string, or an empty list if all fields are valid
        """
        errors = []
        if not d['abbrev'] or len(d['abbrev']) == 0:
            errors.append("- Collection Abbreviation must not be empty/null.")
        if not d['name'] or len(d['name']) == 0:
            errors.append("- Collection name must not be empty/null.")
        if not d['works'] or len(d['works']) == 0:
            errors.append("- Given collection has no works.")
        work_ct = 0
        for w in d['works']:
            work_ct += 1
            if not w:
                errors.append("- Work with index #{} was null, which is not allowed.".format(work_ct))
            if not w['name'] or len(w['name']) == 0:
                errors.append("- Work with index #{} must not have empty/null name.".format(work_ct))
            if not w['filename'] or len(w['filename']) == 0:
                errors.append("- Work with index #{} must not have empty/null filename.".format(work_ct))
            if not w['img'] or len(w['img']) == 0:
                errors.append("- Work with index #{} must not have empty/null image data.".format(work_ct))
        return errors
    #

    validation_errors = validate_add_request(data)
    if len(validation_errors) > 0:
        return '\n'.join(validation_errors)

    # extract useful collection info from data
    collection_abbrev = data['abbrev'].lower()
    collection_name = data['name']
    collection_description = data['description']
    collection_id = Collection.objects.latest('id').id + 1

    # arrange appropriate media URLs
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    media_root = settings.MEDIA_ROOT  # .lstrip('/')
    media_url = media_root # os.path.join(base_dir, media_root)
    temp_url = os.path.join(media_url, 'temp')
    artmonitors_url = os.path.join(media_url, 'artmonitors')
    summaries_url = os.path.join(artmonitors_url, 'summaries')
    thumbnails_url = os.path.join(artmonitors_url, 'thumbnails', collection_abbrev)
    works_url = os.path.join(artmonitors_url, 'works', collection_abbrev)

    print("Finished arranging URLs")

    # sort works by name
    data['works'].sort(key=lambda x: x['name'])

    # clean up the temp media folder before uploading to it
    if not os.path.isdir(temp_url):
        os.mkdir(temp_url)
    else:
        for f in os.listdir(temp_url):
            f_url = os.path.join(temp_url, f)
            if os.path.isdir(f_url):
                os.rmdir(f_url)
            else:
                os.remove(f_url)

    # save raw images to folder
    for w in data['works']:
        with open(os.path.join(temp_url, w['filename']), 'wb') as temp_img_file:
            base64_img = bytes(w['img'], 'utf8')
            raw_img = base64.decodebytes(base64_img)
            temp_img_file.write(raw_img)
        w['pil_image'] = Image.open(os.path.join(temp_url, w['filename']))

    print("Finished saving images to temp folder and loading images")

    # copy all images to the works folder (thus preserving original image format)
    if not os.path.isdir(works_url):
        os.mkdir(works_url)
    for w in data['works']:
        w['file_path'] = os.path.join('artmonitors', 'works', collection_abbrev, w['filename'])
        os.rename(os.path.join(temp_url, w['filename']), os.path.join(works_url, w['filename']))

    print("Finished relocating images to works folder")

    # get and save thumbnails for each image
    for w in data['works']:
        w['thumbnail'] = create_thumbnail(w['pil_image'])
        w['thumbnail_path'] = os.path.join('artmonitors', 'thumbnails', collection_abbrev, w['filename'])
        thumbnail_path = os.path.join(thumbnails_url, w['filename'])
        if not os.path.isdir(thumbnails_url):
            os.makedirs(thumbnails_url)
        w['thumbnail'].save(thumbnail_path, 'JPEG')

    print("Finished creating thumbnails for each image")

    # create and save summary image
    summary_img_abs_url = os.path.join(summaries_url, collection_abbrev + ".gif")
    summary_img_url = os.path.join('artmonitors', 'summaries', collection_abbrev + '.gif')
    create_summary_gif([w['pil_image'] for w in data['works']], summary_img_abs_url)

    print("Finished creating summary .gif for collection")

    # Parse collection description
    parsed_description = re.sub(r'{{collection:(.+?):(.+?)}}',
                                r'''<a href="{% url 'artmonitors:view_collection' coll_abbrev='\1' %}">\2</a>''',
                                collection_description)
    parsed_description = re.sub(r'{{work:(.+?)/(.+?):(.+?)}}',
                                r'''<a href="{% url 'artmonitors:view_work' coll_abbrev='\1' work_name='\2' %}">\3</a>''',
                                parsed_description)
    parsed_description = re.sub(r'{{work:(.+?):(.+?)}}',
                                """<a href="{% url 'artmonitors:view_work' coll_abbrev='""" + collection_abbrev + r"""' work_name='\1' %}">\2</a>""",
                                parsed_description)

    try:
        parsed_desc_template = Template(parsed_description)
    except TemplateSyntaxError as e:
        return "Failed\n" + parsed_description + str(e)

    final_parsed_description = parsed_desc_template.render(Context({}))

    print("Finished parsing collection description")

    # Finally, create actual database objects
    collection = Collection(
        id=collection_id,
        abbrev=collection_abbrev,
        name=collection_name,
        description=final_parsed_description,
        summary=summary_img_url
    )
    collection.save()

    print("Finished saving new Collection object")

    last_work_id = Work.objects.latest('id').id + 1

    for w in data['works']:
        work_name = w['name']
        work_filename = w['filename']
        work_pagename = re.sub(r'[^\x00-\x7f]', r'', work_name.lower().replace(' ', '-').replace(',', '').replace("'", ''))
        work_path = w['file_path']
        work_thumbnail = w['thumbnail_path']
        if w['description']:
            work_description = re.sub(r'{{collection:(.+?):(.+?)}}',
                                      r'''<a href="{% url 'artmonitors:view_collection' coll_abbrev='\1' %}">\2</a>''',
                                      w['description'])
            work_description = re.sub(r'{{work:(.+?)/(.+?):(.+?)}}',
                                      r'''<a href="{% url 'artmonitors:view_work' coll_abbrev='\1' work_name='\2' %}">\3</a>''',
                                      work_description)
            work_description = re.sub(r'{{work:(.+?):(.+?)}}',
                                      """<a href="{% url 'artmonitors:view_work' coll_abbrev='""" + collection_abbrev + r"""' work_name='\1' %}">\2</a>""",
                                      work_description)
            work_desc_template = Template(work_description)
            final_work_description = work_desc_template.render(Context({}))
        else:
            final_work_description = None
        work_id = last_work_id
        work = Work(
            id=work_id,
            collection=collection,
            name=work_name,
            description=final_work_description,
            filename=work_filename,
            pagename=work_pagename,
            path=work_path,
            thumbnail=work_thumbnail,
            featured=False
        )
        work.save()
        last_work_id += 1

        print("  Finished saving work {} with ID {} and path {}".format(work_name, work_id, work_path))
    print("Finished saving new Work objects")
    
    return None
