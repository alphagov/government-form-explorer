from django.contrib import admin

from .models import Task, Form, Organisation, Page, Attachment, History, Download, Snippet

admin.site.register(Task)
admin.site.register(Form)
admin.site.register(Organisation)
admin.site.register(Page)
admin.site.register(Attachment)
admin.site.register(History)
admin.site.register(Download)
admin.site.register(Snippet)
