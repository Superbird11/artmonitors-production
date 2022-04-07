from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import WordReference
from datetime import datetime
from threading import Timer
import json


def clear_cache() -> dict:
    temp = cached_words.copy()
    cached_words.clear()
    return temp


def update_words():
    words = clear_cache()
    now = datetime.now().astimezone()
    for (key, value) in words.items():
        try:
            word = WordReference.objects.get(word=key)
            word.count += value
            word.save()
            print("Wordcount incremented the counter for the word", word, "to", word.count)
        except ObjectDoesNotExist:
            word = WordReference.objects.create(word=key, count=value, lastreset=now)
            word.save()
            print("Wordcount added a new counter for the word", word, "with initial value", word.count)


def async_update_words():
    update_words()
    Timer(300, async_update_words).start()


cached_words = {}
Timer(300, async_update_words).start()


# Create your views here.
def increment_counter(request, word):
    cached_words.setdefault(word, 0)
    cached_words[word] += 1
    print("Wordcount incremented the counter for word", word)
    return HttpResponse(status=201)


def check_counter(request, word):
    update_words()
    try:
        word_obj = WordReference.objects.get(word=word)
        now = datetime.now().astimezone()
        response = {'word': word_obj.word, 'count': word_obj.count, 'lastreset': str(now - word_obj.lastreset)}
        print("Wordcount returned CHECK response", response)
        return HttpResponse(status=201, content=json.dumps(response), content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse(status=404)


def reset_counter(request, word):
    update_words()
    try:
        word_obj = WordReference.objects.get(word=word)
        now = datetime.now().astimezone()
        response = {'word': word_obj.word, 'count': word_obj.count, 'lastreset': str(now - word_obj.lastreset)}
        word_obj.count = 0
        word_obj.lastreset = now
        word_obj.save()
        print("Wordcount reset the counter and returned response", response)
        return HttpResponse(status=201, content=json.dumps(response), content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
