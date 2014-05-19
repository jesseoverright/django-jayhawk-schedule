from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ical/', 'schedule.views.ical'),

    url(r'^team/(?P<slug>[\w\-]+)/$', 'schedule.views.team'),

    url(r'^category/(?P<slug>[\w\- ]+)/$', 'schedule.views.category'),

    url(r'^teams/$', 'schedule.views.all_teams'),
    url(r'^$', 'schedule.views.index'),
    url(r'^(?P<season>[\w\-]+)/(?P<slug>[\w\-]+)/$', 'schedule.views.game')
)
