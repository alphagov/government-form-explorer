from math import log10
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse, Http404
from django.utils.text import slugify
import re
import csv
import requests
from scipy.stats import hmean, gmean
from io import BytesIO
from PIL import Image

from .models import Organisation, Page, Attachment, Download, History, GenericStringTaggedItem, Snippet
from taggit.models import Tag


#'tsv': 'text/tab-separated-values;charset=UTF-8'
content_type = {
    'tsv': 'text/plain'
}

def downloads_stats():
    downloads = Download.objects.values('month') \
        .annotate(attachments=Count('id')) \
        .annotate(downloads=Sum('count')) \
        .order_by("-month")
    counts = [d['downloads'] for d in downloads]

    if len(counts):
        mean = int(round(hmean(counts)))
        peak = max(counts)
    else:
        mean = 0
        peak = 0

    return { 'downloads': downloads, 'counts': counts, 'mean': mean, 'peak': peak }


def count_pages(pages):
    return pages \
            .annotate(attachments=Count('attachment', distinct=True)) \
            .annotate(updates=Count('history', distinct=True)) \
            .order_by('-attachments')


def home(request):
    attachments = Attachment.objects.all()
    stats = downloads_stats()
    count = {
        'organisations': Organisation.objects.annotate(Count('page')).filter(page__count__gt=0).count(),
        'pages': Page.objects.count(),
        'attachments': attachments.count(),
        'size': attachments.aggregate(Sum('size')).get('size__sum'),
        'suffixes': attachments.values('suffix').distinct().count(),
        'refs': attachments.values('ref').distinct().count(),
        'history': History.objects.all().count(),
        'downloads': stats['mean'],
        'tags': len(Tag.objects.all().annotate(count=Count('pages_genericstringtaggeditem_items__id'))),
    }
    return render(request, 'home.html', {'count': count})


def organisations(request):
    organisations = Organisation.objects \
        .order_by('-pages')

    return render(request, 'organisations.html',
                  {'organisations': organisations})


def organisation(request, key=None):
    organisation = Organisation.objects.get(organisation=key)
    pages = count_pages(Page.objects.filter(organisations__organisation__contains=key))
    attachments = Attachment.objects.filter(
        page__organisations__organisation__contains=key)
    return render(request, 'organisation.html',
                  {'organisation': organisation,
                   'pages': pages,
                   'attachments': attachments})


def organisation_pages(request, key=None):
    organisation = Organisation.objects.get(organisation=key)
    pages = count_pages(Page.objects.filter(organisations__organisation__contains=key))
    return render(request, 'organisation_pages.html',
                  {'organisation': organisation,
                   'pages': pages})


def organisation_attachments(request, key=None):
    organisation = Organisation.objects.get(organisation=key)
    attachments = Attachment.objects.filter(
        page__organisations__organisation__contains=key).order_by('-size')
    size = sum(a.size for a in attachments)
    suffixes = attachments.values('suffix').distinct().count()
    return render(request, 'organisation_attachments.html', {
        'organisation': organisation,
        'attachments': attachments,
        'tags': True,
        'size': size,
        'suffixes': suffixes,
    })


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
        'history': history,
        'tags': True,
    })


def attachment_sheets(attachment):
    sheets = []
    if attachment.page_count:
        w = int(log10(attachment.page_count)) + 1
        for n in range(1, min(attachment.page_count + 1, settings.SHEETS_MAX)):
            fmt = '%s/attachment/%s/page-%0' + str(w) + 'd.png'
            src = fmt % (settings.DOCUMENTS_URL, attachment.attachment, n)
            proxy = fmt % ('/documents/', attachment.attachment, n)
            href = "%s#page=%d" % (attachment.url, n)
            sheets.append({'src': src, 'href': href, 'number': n, 'proxy': proxy})
    return sheets


def attachments(request):
    attachments = Attachment.objects.all().order_by('-size')
    suffixes = attachments.values('suffix').distinct().count()
    sizes = [a.size for a in attachments]
    size = sum(sizes)
    return render(request, 'attachments.html', {
        'attachments': attachments,
        'size': size,
        'suffixes': suffixes,
        'sizes': sizes,
    })


def attachment(request, key=None):
    attachment = Attachment.objects.get(attachment=key)
    organisations = Organisation.objects.filter(
        organisation__in=attachment.page.organisations.all())
    downloads = Download.objects.filter(attachment=key)

    counts = [d.count for d in downloads]
    if len(counts):
        mean = int(round(hmean(counts)))
        peak = max(counts)
    else:
        mean = 0
        peak = 0

    # get document from store
    text_path = '/attachment/%s/document.txt' % attachment.attachment
    text_url = '/documents/' + text_path
    proxy_url = settings.DOCUMENTS_URL + text_path
    sheets = attachment_sheets(attachment)

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
        'downloads': downloads,
        'sheets': sheets,
        'mean': mean,
        'peak': peak,
        'counts': counts,
    })


def attachment_downloads(request, key=None, suffix=None):
    attachment = Attachment.objects.get(attachment=key)
    organisations = Organisation.objects.filter(
        organisation__in=attachment.page.organisations.all())
    downloads = Download.objects.filter(attachment=key)

    counts = [d.count for d in downloads]
    if len(counts):
        mean = int(round(hmean(counts)))
        peak = max(counts)
    else:
        mean = 0
        peak = 0

    return render(request, 'attachment_downloads.html', {
        'attachment': attachment,
        'organisations': organisations,
        'downloads': downloads,
        'mean': mean,
        'peak': peak,
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
        response = HttpResponse(content_type=content_type[suffix])
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
    stats = downloads_stats()

    if suffix == "tsv":
        response = HttpResponse(
            content_type='text/tab-separated-values;charset=UTF-8')
        fields = ['month', 'count']
        writer = csv.writer(response, delimiter='\t')
        writer.writerow(fields)
        for row in downloads:
            writer.writerow([str(row[field]) for field in fields])
        return response

    return render(request, 'downloads.html', {
        'downloads': stats['downloads'],
        'mean': stats['mean'],
        'peak': stats['peak'],
        'counts': stats['counts'],
    })


def downloads_month(request, month=None):
    downloads = Download.objects.filter(month=month).order_by("-count")
    counts = [d.count for d in downloads]

    return render(request, 'downloads_month.html', {
        'month': month,
        'downloads': downloads,
        'mean': int(round(gmean(counts))),
        'peak': max(counts),
        'counts': counts,
        'total': sum(counts),
    })


def search(request):
    query = request.GET.get('q', '')
    page_index = int(request.GET.get('page-index', 1))
    page_size = int(request.GET.get('page-size', 100))

    es = settings.ES
    response = es.search(body={
        "from": ((page_index - 1) * page_size),
        "size": page_size,
        "_source": {
             "includes": ["attachment", "name"]
         },
        "query": {
            "query_string": {
                "default_field": "text",
                "query": query
            },
        },
        "highlight": {
             "fields" : {
                 "text" : {
                     "fragment_size" : 300,
                     "number_of_fragments" : 1
                 }
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


def attachments_tags(request, suffix=None):
    tags = Tag.objects.all() \
            .annotate(count=Count('pages_genericstringtaggeditem_items__id')) \
            .order_by('-count', 'name')

    if suffix == "tsv":
        response = HttpResponse(
            content_type='text/tab-separated-values;charset=UTF-8')
        fields = ['tag', 'attachments', 'snippets']
        writer = csv.writer(response, delimiter='\t')
        writer.writerow(fields)
        for tag in tags.all():
            row = {}
            row['tag'] = tag.name
            row['attachments'] = ";".join([str(a.object_id) for a in tag.pages_genericstringtaggeditem_items.all() if str(a.content_type) == 'attachment'])
            row['snippets'] = ";".join([str(a.object_id) for a in tag.pages_genericstringtaggeditem_items.all() if str(a.content_type) == 'snippet'])
            writer.writerow([str(row[field]) for field in fields])
        return response

    return render(request, 'attachments_tags.html', {'tags': tags})



def sample_attachments(request):
    attachments = Attachment.objects

    include_tags = request.GET.get('tags', 'Popular,Form Analysis')
    if include_tags:
        attachments = attachments.filter(tags__name__in=include_tags.split(','))

    exclude_tags = request.GET.get('exclude', 'Guidance,Other')
    if exclude_tags:
        attachments = attachments.exclude(tags__name__in=exclude_tags.split(','))

    return attachments


def sample_tags():
    return [t[3:] for t in map(lambda o: o.slug, Tag.objects.all()) if t[0:3] == 'no-']


def tags_adjacency(request, suffix=None):
    if suffix == "json":
        attachments = sample_attachments(request)
        tags = sample_tags()

        matrix = {}
        for a in attachments:
            atags = [t for t in map(lambda o: o.slug, a.tags.all()) if t in tags]
            for tx in atags:
                if tx not in matrix:
                    matrix[tx] = {}
                for ty in atags:
                    if ty in matrix[tx]:
                        matrix[tx][ty] += 1
                    else:
                        matrix[tx][ty] = 1

        nodes = [{ 'group': 1, 'name': t} for t in tags]
        links = []
        for tx in matrix:
            for ty in matrix[tx]:
                links.append({'source': tags.index(tx), 'target': tags.index(ty), 'value': matrix[tx][ty]})

        return JsonResponse({'nodes': nodes, 'links': links})

    return render(request, 'adjacency.html')


def tags_splits(request):

    taglist = sample_tags()

    tags = {}
    for tag in Tag.objects.filter(slug__in=taglist) \
            .annotate(count=Count('pages_genericstringtaggeditem_items__id')):
        tags[tag.slug] = tag

    no_tags = {}
    for tag in Tag.objects.filter(slug__in=['no-' + t for t in taglist]) \
            .annotate(count=Count('pages_genericstringtaggeditem_items__id')):
        no_tags[tag.slug[3:]] = tag

    splits = []
    for tag in taglist:
        split = {'tags': [], 'total': 0}
        for t in [tags[tag], no_tags[tag]]:
            split['tags'].append({'name': t.name, 'slug': t.slug, 'count': t.count})
            split['total'] += t.count
        splits.append(split)

    splits =  sorted(splits, key=lambda s: s['tags'][0]['count'] / s['total'], reverse=True)

    return render(request, 'splits.html', {'splits': splits})


def attachments_tag(request, slug=None):
    try:
        tag = Tag.objects.get(slug=slug)
    except:
        tag = Tag.objects.get(name=slug)
        return redirect('attachments_tag', slug=tag.slug)

    attachments = Attachment.objects.filter(tags__name__in=[tag.name])

    downloads = Download.objects.filter(attachment__in=attachments).values('month').annotate(total=Sum('count')).order_by('month')

    counts = [d['total'] for d in downloads]
    if len(counts):
        mean = int(round(hmean(counts)))
        peak = max(counts)
    else:
        mean = 0
        peak = 0

    return render(request, 'attachments_tag.html', {
                'tag': tag,
                'tags': True,
                'attachments': attachments,
                'mean': mean,
                'peak': peak,
                'counts': counts,
            })


@login_required
def snippet_create(request, key, n):
    attachment = Attachment.objects.get(attachment=key)
    sheet_number = int(n)
    sheet = attachment_sheets(attachment)[sheet_number-1]

    if request.method == 'POST':
        snippet = Snippet(
            attachment=attachment,
            sheet=sheet_number,
            name=request.POST.get("name", ""),
            text=request.POST.get("text", ""),
            top=int(request.POST.get("top", 0)),
            right=int(request.POST.get("right", 0)),
            bottom=int(request.POST.get("bottom", 0)),
            left=int(request.POST.get("left", 0)),
            url=sheet['src']
        )

        snippet.save()

        for tag in request.POST.get("tags", "").split(","):
            tag = tag.strip()
            if tag:
                snippet.tags.add(tag)

        # grap image, crop and upload to s3
        response = requests.get(snippet.url)
        img = Image.open(BytesIO(response.content))
        img = img.crop((snippet.left, snippet.top, snippet.right, snippet.bottom))
        f = BytesIO()
        img.save(f, 'PNG')
        settings.S3.upload(snippet.path, f, bucket=settings.S3_BUCKET, public=True, content_type='image/png')

        response = HttpResponse(content="", status=303)
        response["Location"] = "%s://%s/snippet/%s" % (request.scheme, request.get_host(), snippet.id)
        return response

    return render(request, 'snippet_create.html',
                   {'attachment': attachment,
                    'sheet': sheet,
                   })


def snippets(request, suffix=None):
    snippets = Snippet.objects.all()

    if suffix == "tsv":
        response = HttpResponse(content_type=content_type[suffix])
        fields = ['snippet', 'name', 'attachment', 'sheet', 'top', 'right', 'bottom', 'left', 'text', 'url', 'tags']
        writer = csv.writer(response, delimiter='\t')
        writer.writerow(fields)
        for snippet in snippets:
            row = {}
            row['snippet'] = snippet.id
            row['attachment'] = snippet.attachment.attachment
            row['name'] = snippet.name
            row['sheet'] = snippet.sheet
            row['top'] = snippet.top
            row['right'] = snippet.right
            row['bottom'] = snippet.bottom
            row['left'] = snippet.left
            row['text'] = '\\n'.join(snippet.text.splitlines())
            row['url'] = snippet.url
            row['tags'] = ";".join(snippet.tags.names())
            writer.writerow([str(row[field]) for field in fields])
        return response

    return render(request, 'snippets.html', { 'snippets': snippets })


def snippet(request, key):
    snippet = Snippet.objects.get(id=int(key))
    return render(request, 'snippet.html', { 'snippet': snippet })


def tagger(request):
    """
          tagger?keys=F:Form,G:Guidance,O:Other&tags=Form%20Analysis
    """
    keys = []
    tags = []
    for k in request.GET.get('keys', '').split(','):
        (key, tag) = k.split(':')
        tags.append(tag)
        keys.append({ 'key': key[0], 'tag': tag })

    attachments = Attachment.objects

    include_tags = request.GET.get('tags', '')
    if include_tags:
        attachments = attachments.filter(tags__name__in=include_tags.split(','))

    exclude_tags = request.GET.get('exclude', '')
    if exclude_tags:
        attachments = attachments.exclude(tags__name__in=exclude_tags.split(','))

    attachments = attachments.exclude(tags__name__in=tags).order_by('?')
    if len(attachments) > 0:
        attachment = attachments[0]
        sheets = attachment_sheets(attachment)

        # get document from store
        text_path = '/attachment/%s/document.txt' % attachment.attachment
        text_url = '/documents/' + text_path
        proxy_url = settings.DOCUMENTS_URL + text_path

        r = requests.get(proxy_url)
        if r.status_code == 200:
            text = r.text.strip()
        else:
            text = ''

        return render(request, 'tagger.html', {
            'attachment': attachment,
            'text': text,
            'text_url': text_url,
            'sheets': sheets,
            'keys': keys,
            'remaining': len(attachments),
        })
    else:
        raise Http404("Nothing to tag")
