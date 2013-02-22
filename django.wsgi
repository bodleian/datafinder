import os
import sys
import django.core.handlers.wsgi

path = '/var/www/datafinder'
if path not in sys.path:
    sys.path.append(path)
    
os.environ['DJANGO_SETTINGS_MODULE'] = 'datafinder.web.settings'


_application = django.core.handlers.wsgi.WSGIHandler()


def application(environ, start_response):
    
    if environ.has_key('REMOTE_USER'):
       os.environ['DF_REMOTE_USER'] = environ['REMOTE_USER']
    return _application(environ, start_response)
