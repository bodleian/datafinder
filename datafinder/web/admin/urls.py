from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
import views
urlpatterns = patterns('',
    url(r'^$',  views.administration),
    url(r'^users/$',  views.manageusers),
    url(r'^users/add/$',  views.adduser),
    url(r'^source/add/$',  views.addsource),
    url(r'^source/edit/$',  views.editsource),
    url(r'^users/edit/$',  views.edituser),
    url(r'^list_sources/$',  views.listsources),
    url(r'^create_source/$',  views.createsource),
    url(r'^register_source/$',  views.registersource),
    url(r'^activate_source/$',  views.activatesource),
    url(r'^save_source/$',  views.savesource),
    url(r'^(?P<source>.*)/approve_source/$',  views.approvesource),
    url(r'^(?P<source>.*)/$',  views.sourceinfo),

  #  url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
  #     'document_root': 'static'}),
                         )

#urlpatterns += staticfiles_urlpatterns()

