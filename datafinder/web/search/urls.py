from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
import views
urlpatterns = patterns('',
    url(r'^$',  views.search),
    url(r'^detailed/$',  views.detailed),
    url(r'^search_tips/$',  views.searchtips),
  #  url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
  #     'document_root': 'static'}),
                         )

#urlpatterns += staticfiles_urlpatterns()