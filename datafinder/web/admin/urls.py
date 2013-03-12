from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
import views
urlpatterns = patterns('',
    url(r'^$',  views.administration),
    url(r'^users/add/',  views.adduser),
    url(r'^users/del/',  views.deluser),
    url(r'^users/edit/',  views.edituser),
    url(r'^source/add/$',  views.addsource),
    url(r'^source/edit/$',  views.editsource),
    url(r'^source/del/$',  views.delsource),
    url(r'^source/approve/$',  views.approvesource),  
    url(r'^(?P<source>.*)/approve_source/$',  views.approvesource),
    url(r'^(?P<source>.*)/$',  views.sourceinfo),

  #  url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
  #     'document_root': 'static'}),
                         )

#urlpatterns += staticfiles_urlpatterns()

