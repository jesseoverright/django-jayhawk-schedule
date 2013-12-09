from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ical/', 'schedule.views.ical'),

    url(r'^team/(?P<slug>[\w\-]+)/$', 'schedule.views.team'),

    url(r'^$', 'schedule.views.index'),
    url(r'^(?P<slug>[\w\-]+)/$', 'schedule.views.game')
)
