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
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/pages$', pages.views.organisation_pages, name='organisation_pages'),
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/attachments/$', pages.views.organisation_attachments, name='organisation_attachments'),
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/history/$', pages.views.history, name='organisation_history'),
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/history/(?P<date>\d{4}-\d{2}-\d{2})$', pages.views.organisation_history_date, name='history'),
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/tags$', pages.views.attachments_tags),
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/refs$', pages.views.refs),
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/suffixes$', pages.views.suffixes),
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/downloads/$', pages.views.downloads),
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/downloads/(?P<month>[\d]{6})$', pages.views.downloads_month),

    url(r'^pages/$', pages.views.pages, name='page'),

    url(r'^pages/history/$', pages.views.history, name='history'),
    url(r'^pages/history.(?P<suffix>[\w]{1,16})$', pages.views.history, name='history'),
    url(r'^pages/history/(?P<date>\d{4}-\d{2}-\d{2})$', pages.views.history_date, name='history'),

    url(r'^page/(?P<key>[:\w\d_-]{1,256})/$', pages.views.page, name='page'),

    url(r'^attachments/$', pages.views.attachments, name='attachment'),
    url(r'^attachments/downloads/$', pages.views.downloads, name='downloads'),
    url(r'^attachments/downloads.tsv$', pages.views.downloads, name='downloads_tsv'),
    url(r'^attachments/downloads/(?P<month>[\d]{6})$', pages.views.downloads_month, name='downloads_month'),
    url(r'^attachments/tags$', pages.views.attachments_tags, name='attachments_tags'),
    url(r'^attachments/tags.(?P<suffix>[\w]{1,16})$', pages.views.attachments_tags, name='attachments_tags'),
    url(r'^attachments/tag/(?P<slug>[\w\d\s:-]{1,128})$', pages.views.attachments_tag, name='attachments_tag'),

    url(r'^tags/splits$', pages.views.tags_splits, name='tags_splits'),
    url(r'^tags/adjacency$', pages.views.tags_adjacency, name='tags_adjacency'),
    url(r'^tags/adjacency.(?P<suffix>[\w]{1,16})$', pages.views.tags_adjacency, name='tags_adjacency'),

    url(r'^attachment/(?P<key>[\d]{1,16})/$', pages.views.attachment, name='attachment'),
    url(r'^attachment/(?P<key>[\d]{1,16})/downloads/$', pages.views.attachment_downloads, name='attachment_downloads'),
    url(r'^attachment/(?P<key>[\d]{1,16})/downloads.(?P<suffix>[\w]{1,16})$', pages.views.attachment_downloads, name='attachment_downloads_json'),
    url(r'^attachment/(?P<key>[\d]{1,16})/tags.(?P<suffix>[\w]{1,16})$', pages.views.attachment_tags, name='attachment_tags'),
    url(r'^attachment/(?P<key>[\d]{1,16})/tag/(?P<name>[\w\d\s:-]{1,128})$', pages.views.attachment_tag, name='attachment_tag'),
    url(r'^attachment/(?P<key>[\d]{1,16})/sheet/(?P<n>[\d]{1,4})/snippets/create$', pages.views.snippet_create, name='snippet_create'),

    url(r'^snippets/$', pages.views.snippets, name='snippets'),
    url(r'^snippets.(?P<suffix>[\w]{1,16})$', pages.views.snippets),

    url(r'^snippet/(?P<key>[\d]{1,16})/$', pages.views.snippet, name='snippet'),

    url(r'^suffixes/$', pages.views.suffixes, name='suffix'),
    url(r'^suffix/(?P<key>[\w\d]{1,16})$', pages.views.suffix, name='suffix'),

    url(r'^refs/$', pages.views.refs, name='ref'),
    url(r'^ref/(?P<key>.{1,256})$', pages.views.ref, name='ref'),

    url(r'^tagger/$', pages.views.tagger, name='tagger'),

    url(r'^google3e69ae69b04281ff\.html$', lambda r: HttpResponse("google-site-verification: google3e69ae69b04281ff.html", content_type="text/plain")),
    url(r'^login$', auth_views.login, name='login'),
    url(r'^login-github$', pages.views.login_github, name='login_github'),
    url(r'^logout$', pages.views.logout, name='logout'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    url(r'^welcome$', pages.views.welcome, name='welcome'),
    url(r'^login-error$', pages.views.login_error, name='login_error'),

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain")),
]
