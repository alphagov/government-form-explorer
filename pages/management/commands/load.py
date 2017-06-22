from django.core.management.base import BaseCommand

import io
import os
import csv
import requests

from ...models import Organisation, Page, Attachment, Download, History

from django.utils.dateparse import parse_datetime
from django.core.exceptions import ObjectDoesNotExist

url = 'https://raw.githubusercontent.com/openregister/government-form-data/master/data/%s.tsv'
field_sep = ';'
sep = '\t'


def tsv_reader(name):
    """ read register-like data from government-form-data TSV"""
    resp = requests.get(url=url % (name))
    resp.raise_for_status()
    return csv.DictReader(io.StringIO(resp.text), delimiter=sep)


def load_organisations():
    print("loading organisations …")
    for row in tsv_reader('organisation'):
        o = Organisation(organisation=row['organisation'], name=row['name'], website=row['website'])
        o.save()


def load_pages():
    print("loading pages …")
    for row in tsv_reader('page'):
        o = Page(page=row['page'], name=row['name'], url=row['url'])
        o.save()
        for organisation in row['organisations'].split(field_sep):
            o.organisations.add(organisation)


def load_attachments():
    print("loading attachments …")
    for row in tsv_reader('attachment'):
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


def load_attachment_metadata():
    print("loading attachment-metadata …")
    for row in tsv_reader('attachment-metadata'):
        try:
            attachment = Attachment.objects.get(attachment=row['attachment'])
        except ObjectDoesNotExist:
            print("unknown attachment", row['attachment'])
            continue
        if row['created']:
            attachment.created = parse_datetime(row['created'])
        if row['modified']:
            attachment.modified = parse_datetime(row['modified'])
        if row['page-count']:
            attachment.page_count = int(row['page-count'])
        attachment.save()


def load_history():
    print("loading history …")
    for row in tsv_reader('history'):
        page = Page.objects.get(page=row['page'])
        o = History(page=page,
                    timestamp=parse_datetime(row['timestamp']),
                    text=row['text'])
        o.save()


def load_downloads():
    print("loading downloads …")
    for row in tsv_reader('download'):
        attachment = Attachment.objects.get(attachment=row['attachment'])
        o = Download(attachment=attachment, month=row['date'], count=int(row['count']))
        o.save()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('table', type=str)

    def handle(self, **options):
        if options['table'] == 'organisations':
            load_organisations()
        elif options['table'] == 'pages':
            load_pages()
        elif options['table'] == 'attachments':
            load_attachments()
        elif options['table'] == 'attachment-metadata':
            load_attachment_metadata()
        elif options['table'] == 'history':
            load_history()
        elif options['table'] == 'downloads':
            load_downloads()
        else:
            raise ValueError('Unknown table', options['table'])
