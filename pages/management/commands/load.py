from django.core.management.base import BaseCommand

import csv

from ...models import Organisation, Page

sep = '\t'


def register_reader(name):
    """ read register-like data """
    return csv.DictReader(open('../government-form-data/data/%s.tsv' % (name)), delimiter=sep)


def load_organisations():
    for row in register_reader('organisation'):
        o = Organisation(organisation=row['organisation'], name=row['name'], website=row['website'])
        o.save()


def load_pages():
    for row in register_reader('page'):
        o = Page(page=row['page'], name=row['name'])
        o.save()


class Command(BaseCommand):

    def handle(self, **options):
        load_organisations()
        load_pages()
