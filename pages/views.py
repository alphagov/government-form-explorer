from django.shortcuts import render

from .models import Page, Organisation


def home(request):
    return render(request, 'home.html')


def pages(request):
    pages = Page.objects.all()
    return render(request, 'pages.html', {'pages': pages})


def page(request, key=None):
    page = Page.objects.get(page=key)
    return render(request, 'page.html', {'page': page})


def organisations(request):
    organisations = Organisation.objects.all()
    return render(request, 'organisations.html', {'organisations': organisations})


def organisation(request, key=None):
    organisation = Organisation.objects.get(organisation=key)
    return render(request, 'organisation.html', {'organisation': organisation})
