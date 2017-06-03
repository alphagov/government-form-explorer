from django.shortcuts import render
from django.db.models import Count

from .models import Organisation, Page, Attachment, Download, History


def count_pages(pages):
    return pages \
            .annotate(attachments=Count('attachment', distinct=True)) \
            .annotate(updates=Count('history', distinct=True)) \
            .order_by('-attachments')


def home(request):
    count = {
        'organisations': Organisation.objects.annotate(Count('page')).filter(page__count__gt=0).count(),
        'pages': Page.objects.count(),
        'attachments': Attachment.objects.count(),
        'suffixes': Attachment.objects.values('suffix').distinct().count(),
    }
    return render(request, 'home.html', {'count': count})


def organisations(request):
    organisations = Organisation.objects \
        .annotate(pages=Count('page', distinct=True)) \
        .annotate(attachments=Count('page__attachment', distinct=True)) \
        .filter(pages__gt=0) \
        .order_by('-pages')
    return render(request, 'organisations.html', {'organisations': organisations})


def organisation(request, key=None):
    organisation = Organisation.objects.get(organisation=key)
    pages = count_pages(Page.objects.filter(organisations__organisation=key))
    return render(request, 'organisation.html', {'organisation': organisation, 'pages': pages})


def organisation_attachments(request, key=None):
    organisation = Organisation.objects.get(organisation=key)
    attachments = Attachment.objects.filter(page__organisations__organisation__contains=key).order_by('-size')
    return render(request, 'organisation_attachments.html', {'organisation': organisation, 'attachments': attachments})


def pages(request):
    pages = count_pages(Page.objects)
    return render(request, 'pages.html', {'pages': pages})


def page(request, key=None):
    page = Page.objects.get(page=key)
    organisations = Organisation.objects.filter(organisation__in=page.organisations.all())
    attachments = Attachment.objects.filter(page=key).order_by('name')
    history = History.objects.filter(page=key)
    return render(request, 'page.html', {
        'page': page,
        'organisations': organisations,
        'attachments': attachments,
        'history': history})


def attachments(request):
    attachments = Attachment.objects.all().order_by('-size')
    return render(request, 'attachments.html', {'attachments': attachments})


def attachment(request, key=None):
    attachment = Attachment.objects.get(attachment=key)
    organisations = Organisation.objects.filter(organisation__in=attachment.page.organisations.all())
    downloads = Download.objects.filter(attachment=key)
    return render(request, 'attachment.html', {
        'attachment': attachment,
        'organisations': organisations,
        'downloads': downloads})


def suffixes(request):
    suffixes = Attachment.objects.values('suffix').order_by().annotate(Count('suffix')).order_by("-suffix__count")
    return render(request, 'suffixes.html', {'suffixes': suffixes})


def suffix(request, key=None):
    attachments = Attachment.objects.filter(suffix=key)
    return render(request, 'suffix.html', {'suffix': key, 'attachments': attachments})


def refs(request):
    refs = Attachment \
        .objects.values('ref') \
        .exclude(ref__isnull=True) \
        .exclude(ref__exact='') \
        .order_by().annotate(Count('ref')) \
        .order_by("-ref__count")
    return render(request, 'refs.html', {'refs': refs})


def ref(request, key=None):
    attachments = Attachment.objects.filter(ref=key)
    return render(request, 'ref.html', {'ref': key, 'attachments': attachments})
