from django.conf.urls import include, url
from django.contrib import admin
import pages.views

admin.autodiscover()

urlpatterns = [

    url(r'^$', pages.views.home),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^organisations/$', pages.views.organisations, name='organisation'),
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/$', pages.views.organisation, name='organisation'),

    url(r'^pages/$', pages.views.pages, name='page'),
    url(r'^page/(?P<key>[:\w\d_-]{1,256})/$', pages.views.page, name='page'),

    url(r'^attachments/$', pages.views.attachments, name='attachment'),
    url(r'^attachment/(?P<key>[\d]{1,16})/$', pages.views.attachment, name='attachment'),

    url(r'^suffixes/$', pages.views.suffixes, name='suffix'),
    url(r'^suffix/(?P<key>[\w\d]{1,16})$', pages.views.suffix, name='suffix'),

    url(r'^refs/$', pages.views.refs, name='ref'),
    url(r'^ref/(?P<key>.{1,256})$', pages.views.ref, name='ref'),
]
