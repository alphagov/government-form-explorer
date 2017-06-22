from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from django.utils.text import slugify
import csv
import requests

from .models import Organisation, Page, Attachment, Download, History
from taggit.models import Tag


def count_pages(pages):
    return pages \
            .annotate(attachments=Count('attachment', distinct=True)) \
            .annotate(updates=Count('history', distinct=True)) \
            .order_by('-attachments')


def home(request):
    count = {
        'organisations':
        Organisation.objects.annotate(Count('page')).filter(
            page__count__gt=0).count(),
        'pages':
        Page.objects.count(),
        'attachments':
        Attachment.objects.count(),
        'suffixes':
        Attachment.objects.values('suffix').distinct().count(),
        'refs':
        Attachment.objects.values('ref').distinct().count(),
        'history':
        History.objects.all().count(),
        'downloads':
        Download.objects.all().aggregate(Sum('count')).get('count__sum'),
    }
    return render(request, 'home.html', {'count': count})


def organisations(request):
    organisations = Organisation.objects \
        .annotate(pages=Count('page', distinct=True)) \
        .annotate(attachments=Count('page__attachment', distinct=True)) \
        .filter(pages__gt=0) \
        .order_by('-pages')
    return render(request, 'organisations.html',
                  {'organisations': organisations})


def organisation(request, key=None):
    organisation = Organisation.objects.get(organisation=key)
    pages = count_pages(Page.objects.filter(organisations__organisation=key))
    return render(request, 'organisation.html',
                  {'organisation': organisation,
                   'pages': pages})


def organisation_attachments(request, key=None):
    organisation = Organisation.objects.get(organisation=key)
    attachments = Attachment.objects.filter(
        page__organisations__organisation__contains=key).order_by('-size')
    return render(request, 'organisation_attachments.html',
                  {'organisation': organisation,
                   'attachments': attachments})


def pages(request):
    pages = count_pages(Page.objects)
    return render(request, 'pages.html', {'pages': pages})


def page(request, key=None):
    page = Page.objects.get(page=key)
    organisations = Organisation.objects.filter(
        organisation__in=page.organisations.all())
    attachments = Attachment.objects.filter(page=key).order_by('name')
    history = History.objects.filter(page=key)
    return render(request, 'page.html', {
        'page': page,
        'organisations': organisations,
        'attachments': attachments,
        'history': history
    })


def attachments(request):
    attachments = Attachment.objects.all().order_by('-size')
    return render(request, 'attachments.html', {'attachments': attachments})


def attachment(request, key=None):
    attachment = Attachment.objects.get(attachment=key)
    organisations = Organisation.objects.filter(
        organisation__in=attachment.page.organisations.all())
    downloads = Download.objects.filter(attachment=key)

    # get document from store
    text_path = '/attachment/%s/document.txt' % attachment.attachment
    text_url = '/documents/' + text_path
    proxy_url = settings.DOCUMENTS_URL + text_path

    r = requests.get(proxy_url)
    if r.status_code == 200:
        text = r.text.strip()
    else:
        text = ''

    return render(request, 'attachment.html', {
        'attachment': attachment,
        'text': text,
        'text_url': text_url,
        'organisations': organisations,
        'downloads': downloads
    })


def suffixes(request):
    suffixes = Attachment.objects.values('suffix').order_by().annotate(
        Count('suffix')).order_by("-suffix__count")
    return render(request, 'suffixes.html', {'suffixes': suffixes})


def suffix(request, key=None):
    attachments = Attachment.objects.filter(suffix=key)
    return render(request, 'suffix.html',
                  {'suffix': key,
                   'attachments': attachments})


def refs(request):
    refs = Attachment.objects \
        .values('ref') \
        .exclude(ref__isnull=True) \
        .exclude(ref__exact='') \
        .order_by().annotate(Count('ref')) \
        .order_by("-ref__count")
    return render(request, 'refs.html', {'refs': refs})


def ref(request, key=None):
    attachments = Attachment.objects.filter(ref=key)
    return render(request, 'ref.html',
                  {'ref': key,
                   'attachments': attachments})


def history(request, suffix=None):
    history = History.objects \
        .extra({'date': "date(timestamp)"}) \
        .values('date') \
        .annotate(count=Count('id')) \
        .order_by("-date")

    if suffix == "tsv":
        response = HttpResponse(
            content_type='text/tab-separated-values;charset=UTF-8')
        fields = ['date', 'count']
        writer = csv.writer(response, delimiter='\t')
        writer.writerow(fields)
        for row in history:
            writer.writerow([str(row[field]) for field in fields])
        return response

    return render(request, 'history.html', {'history': history})


def history_date(request, date=None):
    history = History.objects.filter(timestamp__startswith=date)
    return render(request, 'history_date.html',
                  {'date': date,
                   'history': history})


def downloads(request, suffix=None):
    downloads = Download.objects.values('month') \
        .annotate(attachments=Count('id')) \
        .annotate(downloads=Sum('count')) \
        .order_by("-month")

    if suffix == "tsv":
        response = HttpResponse(
            content_type='text/tab-separated-values;charset=UTF-8')
        fields = ['month', 'count']
        writer = csv.writer(response, delimiter='\t')
        writer.writerow(fields)
        for row in downloads:
            writer.writerow([str(row[field]) for field in fields])
        return response

    return render(request, 'downloads.html', {'downloads': downloads})


def search(request):
    query = request.GET.get('q', '')
    page_index = int(request.GET.get('page-index', 1))
    page_size = int(request.GET.get('page-size', 100))

    es = settings.ES
    response = es.search(body={
        "from": ((page_index - 1) * page_size),
        "size": page_size,
        "query": {
            "query_string": {
                "default_field": "text",
                "query": query
            }
        }
    })

    hits = []
    for h in response['hits']['hits']:
        hit = {}
        for key, value in h.items():
            if key.startswith('_'):
                key = key[1:]
            hit[key] = value
        hits.append(hit)

    page_count = (response['hits']['total'] + page_size - 1) // page_size

    if page_index <= 1:
        page_previous = None
    else:
        page_previous = page_index - 1

    if page_index >= page_count:
        page_next = None
    else:
        page_next = page_index + 1

    return render(request, 'search.html', {
        'query': query,
        'response': response,
        'hits': hits,
        'page_index': page_index,
        'page_count': page_count,
        'page_next': page_next,
        'page_previous': page_previous,
        'page_size': page_size
    })


@login_required
def welcome(request):
    return render(request, 'welcome.html')


def login_github(request):
    return render(request, 'registration/login_github.html')


def logout(request):
    auth_logout(request)
    return redirect('/')


def login_error(request):
    return render(request, 'login-error.html', status=401)


def attachment_tags(request, key=None, suffix=None):
    attachment = Attachment.objects.get(attachment=key)

    if suffix == "json":
        tags = [tag.name for tag in attachment.tags.all().order_by('slug')]
        return JsonResponse({'tags': tags})

    raise Http404("Not found")


@login_required
def attachment_tag(request, key=None, name=None):
    attachment = Attachment.objects.get(attachment=key)

    if request.method == 'PUT':
        attachment.tags.add(name)
        return HttpResponse(status=204)

    if request.method == 'DELETE':
        attachment.tags.remove(name)
        return HttpResponse(status=204)

    return HttpResponse(status=200)


def attachments_tags(request):
    tags = Tag.objects.all() \
            .annotate(count=Count('pages_genericstringtaggeditem_items__id')) \
            .order_by('-count', 'name')
    return render(request, 'attachments_tags.html', {'tags': tags})


def attachments_tag(request, slug=None):
    try:
        tag = Tag.objects.get(slug=slug)
    except:
        tag = Tag.objects.get(name=slug)
        return redirect('attachments_tag', slug=tag.slug)

    attachments = Attachment.objects.filter(tags__name__in=[tag.name])
    return render(request, 'attachments_tag.html',
                  {'tag': tag,
                   'attachments': attachments})

