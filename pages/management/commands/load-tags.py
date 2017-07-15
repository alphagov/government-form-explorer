from django.core.management.base import BaseCommand

import io
import os
import csv
import requests

from ...models import Attachment

url = 'https://raw.githubusercontent.com/openregister/government-form-data/master/data/tag.tsv'
field_sep = ';'
sep = '\t'


def tsv_reader():
    """ read register-like data from government-form-data TSV"""
    resp = requests.get(url=url)
    resp.raise_for_status()
    return csv.DictReader(io.StringIO(resp.text), delimiter=sep)


def load_attachment_tags():
    print("loading attachment tags …")
    for row in tsv_reader():
        for attachment in row['attachments'].split(';'):
            try:
                a = Attachment.objects.get(attachment=attachment)
                a.tags.add(row['tag'])
                a.save()
            except:
                print('Missing attachment: ', attachment)


class Command(BaseCommand):

    def handle(self, **options):
        load_attachment_tags()
