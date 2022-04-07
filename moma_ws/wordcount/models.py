__author__ = "Louis Jacobowitz <ldjacobowitzer@gmail.com>"

from django.db import models


# Create your models here.
class WordReference(models.Model):
    def __str__(self):
        return f"'{self.word}': {self.count} (last reset: {self.lastreset})"
        pass

    word = models.CharField(max_length=31, primary_key=True)
    count = models.IntegerField()
    lastreset = models.DateTimeField()
