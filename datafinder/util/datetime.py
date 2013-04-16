
from __future__ import absolute_import

import pytz
import datetime

try:
    from django.conf import settings
except ImportError:
    timezone = pytz.utc
else:
    timezone = pytz.timezone(settings.TIME_ZONE)

def now():
    return pytz.utc.localize(datetime.datetime.utcnow()).astimezone(timezone)

