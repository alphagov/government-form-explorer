from django.db import models


class Organisation(models.Model):
    organisation = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=256)
    website = models.CharField(max_length=256)


class Page(models.Model):
    page = models.CharField(max_length=256, primary_key=True)
    name = models.CharField(max_length=256)
    url = models.CharField(max_length=256)
    organisations = models.ManyToManyField(Organisation)
