from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',       
  url(r'^', include('datafinder.web.core.urls', 'core')),
  url(r'^contribute/$', include('datafinder.web.contribute.urls', 'contribute')),
  url(r'^search/', include('datafinder.web.search.urls', 'search')),
  url(r'^admin/', include('datafinder.web.admin.urls', 'admin')),
  url(r'^log', include('datafinder.web.webauth.urls', 'webauth')),
     )

urlpatterns += staticfiles_urlpatterns()

  #  url(r'^ogin/', controller='account', action='login')
  #url(r'^cookies/', controller='cookies', action='index')
  #url(r'^about/', controller='about', action='index')
  #url(r'^list_sources/', controller='list_sources', action='index')
  #url(r'^contribute/', controller='contribute', action='index')    
  #url(r'^create_source/', controller='create_source', action='index')
  #url(r'^{source}/approve_source/', controller='create_source', action='approve')
  #url(r'^admin/save_source/', controller='admin', action='savesource')
  #url(r'^admin/register_source/', controller='admin', action='registersource')
  #url(r'^admin/', controller='admin', action='index')
  #url(r'^{source}/admin/', controller='admin', action='sourceinfo')
    ##map.connect(r'^manage_source', controller='manage_source', action='index')
  #url(r'^manage_source/{source}/', controller='manage_source', action='managesource')

    # Examples:
    # url(r'^$', 'datafinder.views.home', name='home'),
    # url(r'^datafinder/', include('datafinder.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    
