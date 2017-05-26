from django.conf.urls import include, url
from django.contrib import admin
import pages.views

admin.autodiscover()

urlpatterns = [

    url(r'^$', pages.views.home),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^pages/$', pages.views.pages, name='page'),
    url(r'^page/(?P<key>[:\w\d_-]{1,256})/$', pages.views.page, name='page'),

    url(r'^organisations/$', pages.views.organisations, name='organisation'),
    url(r'^organisation/(?P<key>[:\w\d_-]{1,256})/$', pages.views.organisation, name='organisation'),
]
