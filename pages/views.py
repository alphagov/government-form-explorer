from django.shortcuts import render
from django.db.models import Count

from .models import Organisation, Page, Attachment, Download, History


def home(request):
    return render(request, 'home.html')


def organisations(request):
    organisations = Organisation.objects.annotate(Count('page')).filter(page__count__gt=0).order_by('-page__count')
    return render(request, 'organisations.html', {'organisations': organisations})


def organisation(request, key=None):
    organisation = Organisation.objects.get(organisation=key)
    pages = Page.objects.filter(organisations__organisation=key)
    return render(request, 'organisation.html', {'organisation': organisation, 'pages': pages})


def pages(request):
    pages = Page.objects.annotate(attachments=Count('attachment', distinct=True)).annotate(updates=Count('history', distinct=True)).order_by('-attachments')
    return render(request, 'pages.html', {'pages': pages})


def page(request, key=None):
    page = Page.objects.get(page=key)
    organisations = Organisation.objects.filter(organisation__in=page.organisations.all())
    attachments = Attachment.objects.filter(page=key)
    history = History.objects.filter(page=key)
    return render(request, 'page.html', {
        'page': page,
        'organisations': organisations,
        'attachments': attachments,
        'history': history})


def attachments(request):
    attachments = Attachment.objects.all()
    return render(request, 'attachments.html', {'attachments': attachments})


def attachment(request, key=None):
    attachment = Attachment.objects.get(attachment=key)
    downloads = Download.objects.filter(attachment=key)
    return render(request, 'attachment.html', {'attachment': attachment, 'downloads': downloads})


def suffixes(request):
    suffixes = Attachment.objects.values('suffix').order_by().annotate(Count('suffix')).order_by("-suffix__count")
    return render(request, 'suffixes.html', {'suffixes': suffixes})


def suffix(request, key=None):
    attachments = Attachment.objects.filter(suffix=key)
    return render(request, 'suffix.html', {'suffix': key, 'attachments': attachments})


def refs(request):
    refs = Attachment.objects.values('ref').exclude(ref__isnull=True).exclude(ref__exact='').order_by().annotate(Count('ref')).order_by("-ref__count")
    return render(request, 'refs.html', {'refs': refs})


def ref(request, key=None):
    attachments = Attachment.objects.filter(ref=key)
    return render(request, 'ref.html', {'ref': key, 'attachments': attachments})
