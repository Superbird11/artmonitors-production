"""
A python file declaring the models used in this project.
Since this project is exclusively intended to host files of
personal importance and little else, the contained models
are very simple.
"""
__author__ = "Louis Jacobowitz <ldjacobowitzer@gmail.com>"

from django.db import models
import os

# Create your models here.


def generate_filename(instance, filename):
    print(filename)
    if instance.folder and len(instance.folder) > 0:
        print(os.path.join('personal', instance.folder, filename))
        return os.path.join('personal', instance.folder, filename)
    else:
        return 'personal/{}'.format(filename)


class PersonalFile(models.Model):
    """
    A model type representing a single file. Contains only that
    file object.
    """
    def __str__(self):
        return "{} ---> {}".format(self.name, str(self.file))

    """ The url for accessing this file """
    name = models.CharField(max_length=200)
    """ A description for this project """
    description = models.TextField(blank=True, null=True)
    """ Whether this item should be displayed on the projects index """
    display = models.BooleanField(default=True)
    """ A folder for this object to be placed in """
    folder = models.CharField(max_length=200, blank=True, null=True, default=None)
    """ The actual media url of the file """
    file = models.FileField(upload_to=generate_filename)
