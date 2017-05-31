from django.core.management.base import BaseCommand

import os
import csv

from ...models import Organisation, Page, Attachment, Download, History

from django.utils.dateparse import parse_datetime

field_sep = ';'
sep = '\t'


def register_reader(name):
    """ read register-like data """
    # TBD: fetch from GitHub
    return csv.DictReader(open('../government-form-data/data/%s.tsv' % (name)), delimiter=sep)


def load_organisations():
    print("loading organisations …")
    for row in register_reader('organisation'):
        o = Organisation(organisation=row['organisation'], name=row['name'], website=row['website'])
        o.save()


def load_pages():
    print("loading pages …")
    for row in register_reader('page'):
        o = Page(page=row['page'], name=row['name'], url=row['url'])
        o.save()
        for organisation in row['organisations'].split(field_sep):
            o.organisations.add(organisation)


def load_attachments():
    print("loading attachments …")
    for row in register_reader('attachment'):
        filename, suffix = os.path.splitext(row['filename'])
        page = Page.objects.get(page=row['page'])
        o = Attachment(attachment=row['attachment'],
                       filename=row['filename'],
                       page=page,
                       name=row['name'],
                       ref=row['ref'],
                       url=row['url'],
                       size=int(row['size']),
                       mime=row['mime'],
                       magic=row['magic'],
                       suffix=suffix[1:])
        o.save()


def load_history():
    print("loading history …")
    for row in register_reader('history'):
        page = Page.objects.get(page=row['page'])
        o = History(page=page,
                     timestamp=parse_datetime(row['timestamp']),
                     text=row['text'])
        o.save()


def load_downloads():
    print("loading downloads …")
    for row in register_reader('download'):
        attachment = Attachment.objects.get(attachment=row['attachment'])
        o = Download(attachment=attachment, month=row['date'], count=int(row['count']))
        o.save()


class Command(BaseCommand):

    def handle(self, **options):
        load_organisations()
        load_pages()
        load_attachments()
        load_history()
        load_downloads()
