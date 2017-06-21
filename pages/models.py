from django.db import models
from taggit.managers import TaggableManager


class Task(models.Model):
    name = models.CharField(max_length=256, primary_key=True)


class Form(models.Model):
    form = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=16)
    task = models.ForeignKey(Task)


class Organisation(models.Model):
    organisation = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=256)
    website = models.CharField(max_length=256)


class Page(models.Model):
    page = models.CharField(max_length=256, primary_key=True)
    name = models.CharField(max_length=256)
    url = models.CharField(max_length=256)
    organisations = models.ManyToManyField(Organisation)


class Attachment(models.Model):
    attachment = models.CharField(max_length=8, primary_key=True)
    filename = models.CharField(max_length=256)
    page = models.ForeignKey(Page)
    name = models.CharField(max_length=256)
    ref = models.CharField(max_length=256)
    url = models.CharField(max_length=256)
    size = models.IntegerField()
    mime = models.CharField(max_length=128)
    magic = models.CharField(max_length=1024)
    suffix = models.CharField(max_length=16)
    form = models.ForeignKey(Form, null=True)
    tags = TaggableManager()


class History(models.Model):
    page = models.ForeignKey(Page)
    timestamp = models.DateTimeField()
    text = models.CharField(max_length=1024)


class Download(models.Model):
    class Meta:
        unique_together = (('attachment', 'month'),)

    attachment = models.ForeignKey(Attachment)
    month = models.CharField(max_length=6)
    count = models.IntegerField()
