from django.shortcuts import render

from .models import Page, Organisation


def home(request):
    return render(request, 'home.html')


def pages(request):
    pages = Page.objects.all()
    return render(request, 'pages.html', {'pages': pages})


def page(request, key=None):
    page = Page.objects.get(page=key)
    organisations = Organisation.objects.filter(organisation__in=page.organisations.all())
    return render(request, 'page.html', {'page': page, 'organisations': organisations})


def organisations(request):
    organisations = Organisation.objects.all()
    return render(request, 'organisations.html', {'organisations': organisations})


def organisation(request, key=None):
    organisation = Organisation.objects.get(organisation=key)
    pages = Page.objects.filter(organisations__organisation=key)
    return render(request, 'organisation.html', {'organisation': organisation, 'pages': pages})
