from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth import views as auth_views
import pages.views

from httpproxy.views import HttpProxy

admin.autodiscover()

urlpatterns = [

    url(r'^$', pages.views.home),

    url(r'^search$', pages.views.search, name='search'),

    url(r'^documents/(?P<url>.*)$', HttpProxy.as_view(base_url=settings.DOCUMENTS_URL)),

    url(r'^organisations/$', pages.views.organisations, name='organisations'),
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/$', pages.views.organisation, name='organisation'),
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/attachments/$', pages.views.organisation_attachments, name='organisation'),

    url(r'^pages/$', pages.views.pages, name='page'),

    url(r'^pages/history/$', pages.views.history, name='history'),
    url(r'^pages/history.(?P<suffix>[\w]{1,16})$', pages.views.history, name='history'),
    url(r'^pages/history/(?P<date>\d{4}-\d{2}-\d{2})$', pages.views.history_date, name='history'),

    url(r'^page/(?P<key>[:\w\d_-]{1,256})/$', pages.views.page, name='page'),

    url(r'^attachments/$', pages.views.attachments, name='attachment'),
    url(r'^attachments/downloads/$', pages.views.downloads, name='downloads'),
    url(r'^attachments/downloads.(?P<suffix>[\w]{1,16})$', pages.views.downloads, name='downloads'),

    url(r'^attachment/(?P<key>[\d]{1,16})/$', pages.views.attachment, name='attachment'),
    url(r'^attachment/(?P<key>[\d]{1,16})/tags.(?P<suffix>[\w]{1,16})$', pages.views.attachment_tags, name='attachment_tags'),
    url(r'^attachment/(?P<key>[\d]{1,16})/tag/(?P<tag>[\w]{1,256})$', pages.views.attachment_tag, name='attachment_tag'),

    url(r'^suffixes/$', pages.views.suffixes, name='suffix'),
    url(r'^suffix/(?P<key>[\w\d]{1,16})$', pages.views.suffix, name='suffix'),

    url(r'^refs/$', pages.views.refs, name='ref'),
    url(r'^ref/(?P<key>.{1,256})$', pages.views.ref, name='ref'),

    url(r'^google3e69ae69b04281ff\.html$', lambda r: HttpResponse("google-site-verification: google3e69ae69b04281ff.html", content_type="text/plain")),
    url(r'^login$', auth_views.login, name='login'),
    url(r'^login-github$', pages.views.login_github, name='login_github'),
    url(r'^logout$', pages.views.logout, name='logout'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    url(r'^welcome$', pages.views.welcome, name='welcome'),
    url(r'^login-error$', pages.views.login_error, name='login_error'),

    url(r'^admin/', include(admin.site.urls)),
]
