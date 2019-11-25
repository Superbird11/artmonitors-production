"""
A python file declaring the database models used in this project - in this case,
Collections and Works
"""
__author__ = "Louis Jacobowitz <ldjacobowitzer@gmail.com>"

from django.db import models

# Create simple methods to return file names for models


def get_summary_filename(instance, filename):
    return 'artmonitors/summaries/{}'.format(str(instance.abbrev))


def get_work_filename(instance, filename):
    return 'artmonitors/works/{}/{}'.format(str(instance.collection.abbrev), str(instance.filename))


def get_thumbnail_filename(instance, filename):
    return 'artmonitors/thumbnails/{}/{}'.format(str(instance.collection.abbrev), str(instance.filename))


def group_works(works, group_size):
    """
    Bundles the given list of works into a list of lists, each one sized
    according to group_size, truncating the last group if needed
    :param works: a list of Work instances
    :param group_size: the intended size of each group
    :return: a list of lists of Work instances, where each sublist has size group_size
    """
    for i in range(0, len(works), group_size):
        yield works[i:i + group_size] if i + group_size < len(works) else works[i:]


# create models themselves


class Collection(models.Model):
    """
    A structure representing a Collection, with an associated index/ID ,
    an abbreviation, a full name, and a description
    """
    def __str__(self):
        return "{0} - {1}".format(str(self.abbrev).upper(), str(self.name))

    def __lt__(self, other):
        return self.id < other.id

    """ A primary key ID """
    id = models.FloatField(primary_key=True, blank=True)

    """ A three-to-six-character collection abbreviation, e.g. "macs" """
    abbrev = models.CharField('abbreviation', max_length=10, default=None)

    """ An expanded name of the collection, e.g. "Modern Art Color Study" """
    name = models.CharField(max_length=100, default=None)

    """ A description of this collection. Can be null. """
    description = models.TextField(null=True, blank=True, default=None)

    """ A path to a summary GIF of all the images in this collection """
    summary = models.ImageField(blank=True, upload_to=get_summary_filename, default=None)


class Work(models.Model):
    """
    A structure representing a Work of modern art, with an associated
    index/id, a collection, a name, a file, a thumbnail
    """
    def __str__(self):
        return "{0}/{1}".format(str(self.collection.abbrev).upper(), str(self.name))

    def __lt__(self, other):
        return self.id < other.id

    """ A primary key ID """
    id = models.IntegerField(primary_key=True)

    """ The Collection object that this work is in """
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    """ The name of this work, e.g. "Beneath A Blue Sky" """
    name = models.CharField(max_length=100, default=None)

    """ The filename of this work, e.g. "Beneath A Blue Sky.jpg" """
    filename = models.CharField(max_length=100, default=None)

    """ The pagename of this work, lowercase without spaces, e.g. "beneath-a-blue-sky" """
    pagename = models.CharField(max_length=100, default=None)

    """ A description of this work. May be null. """
    description = models.TextField(null=True, blank=True, default=None)

    """ A path to the actual image file of this work """
    path = models.ImageField(upload_to=get_work_filename, default=None)

    """ A path to the thumbnail image file of this work """
    thumbnail = models.ImageField(upload_to=get_thumbnail_filename, default=None)

    """ A boolean deciding whether or not this work is able to be featured on the front page """
    featured = models.BooleanField(default=False)


class TemplateCollection(models.Model):
    """
    A structure representing a Collection yet to be uploaded.
    an abbreviation, a full name, and a description
    """

    def __str__(self):
        return "{0} - Template - {1} - {2}".format(self.id, str(self.abbrev).upper(), str(self.name))

    def __lt__(self, other):
        return self.id < other.id

    """ A primary key ID """
    id = models.FloatField(primary_key=True, blank=True)

    """ A three-to-six-character collection abbreviation, e.g. "macs" """
    abbrev = models.CharField('abbreviation', max_length=10, default=None, editable=False)

    """ An expanded name of the collection, e.g. "Modern Art Color Study" """
    name = models.CharField(max_length=100, default=None, editable=False)

    """ A description of this collection. Can be null. """
    description = models.TextField(null=True, blank=True, default=None, editable=False)

    """ The JSON data that was part of this request. """
    json_data = models.TextField(editable=False)
