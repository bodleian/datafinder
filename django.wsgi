import os
import sys
import django.core.handlers.wsgi

path = '/var/www/datafinder'
if path not in sys.path:
    sys.path.append(path)
    
os.environ['DJANGO_SETTINGS_MODULE'] = 'datafinder.web.settings'


application = django.core.handlers.wsgi.WSGIHandler()

