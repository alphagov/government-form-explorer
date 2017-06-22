from django.core.management.base import BaseCommand

import io
import os
import csv
import requests

from ...models import Attachment

url = 'https://raw.githubusercontent.com/openregister/government-form-data/master/tags/%s.tsv'
field_sep = ';'
sep = '\t'


def tsv_reader(name):
    """ read register-like data from government-form-data TSV"""
    resp = requests.get(url=url % (name))
    resp.raise_for_status()
    return csv.DictReader(io.StringIO(resp.text), delimiter=sep)


def load_attachment_tags(name):
    print("loading %s attachment tags …", name)
    for row in tsv_reader(name):
        attachment = Attachment.objects.get(attachment=row['attachment'])
        attachment.tags.add(row['tag'])
        attachment.save()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)

    def handle(self, **options):
        load_attachment_tags(options['name'])
