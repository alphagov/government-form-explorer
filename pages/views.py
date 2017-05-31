from django.shortcuts import render

from .models import Organisation, Page, Attachment, Download, History


def home(request):
    return render(request, 'home.html')


def organisations(request):
    organisations = Organisation.objects.all()
    return render(request, 'organisations.html', {'organisations': organisations})


def organisation(request, key=None):
    organisation = Organisation.objects.get(organisation=key)
    pages = Page.objects.filter(organisations__organisation=key)
    return render(request, 'organisation.html', {'organisation': organisation, 'pages': pages})


def pages(request):
    pages = Page.objects.all()
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
    attachments = Attachment.objects.all()
    suffixes = {}
    for attachment in attachments:
        suffixes[attachment.suffix] = suffixes.get(attachment.suffix, 0) + 1
    suffixes = sorted(suffixes.items())

    return render(request, 'suffixes.html', {'suffixes': suffixes})


def suffix(request, key=None):
    attachments = Attachment.objects.filter(suffix=key)
    return render(request, 'suffix.html', {'suffix': key, 'attachments': attachments})


def refs(request):
    attachments = Attachment.objects.all()
    refs = {}
    for attachment in attachments:
        refs[attachment.ref] = refs.get(attachment.ref, 0) + 1
    refs = sorted(refs.items())

    return render(request, 'refs.html', {'refs': refs})


def ref(request, key=None):
    attachments = Attachment.objects.filter(ref=key)
    return render(request, 'ref.html', {'ref': key, 'attachments': attachments})
