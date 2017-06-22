from django.db import models
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager
from taggit.models import CommonGenericTaggedItemBase, TaggedItemBase


class GenericStringTaggedItem(CommonGenericTaggedItemBase, TaggedItemBase):
    object_id = models.CharField(max_length=256, verbose_name=_('Object id'), db_index=True)


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

    def __str__(self):
       return self.organisation + " " + self.name


class Page(models.Model):
    page = models.CharField(max_length=256, primary_key=True)
    name = models.CharField(max_length=256)
    url = models.CharField(max_length=256)
    organisations = models.ManyToManyField(Organisation)

    def __str__(self):
       return self.page


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
    tags = TaggableManager(through=GenericStringTaggedItem)

    def __str__(self):
       return self.attachment


class History(models.Model):
    page = models.ForeignKey(Page)
    timestamp = models.DateTimeField()
    text = models.CharField(max_length=1024)

    def __str__(self):
       return str(self.page)

class Download(models.Model):
    class Meta:
        unique_together = (('attachment', 'month'),)

    attachment = models.ForeignKey(Attachment)
    month = models.CharField(max_length=6)
    count = models.IntegerField()

    def __str__(self):
       return str(self.attachment)
