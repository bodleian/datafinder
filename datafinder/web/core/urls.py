from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
import views
urlpatterns = patterns('',
    url(r'^$',  views.home),
    #url(r'^home/$',  views.home),
    url(r'^browse/$', views.browse),
    url(r'^about/$',  views.about),
    url(r'^help/$',  views.help),
    url(r'^contact/$',  views.contact),
    url(r'^cookies/$',  views.cookies),
    url(r'^terms-conditions/$',  views.termsconditions),
    url(r'^privacy/$',  views.privacy),
    url(r'^accessibility/$',  views.accessibility),
    url(r'^myrecords/$',  views.myrecords),
  #  url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
  #     'document_root': 'static'}),
                         )

#urlpatterns += staticfiles_urlpatterns()