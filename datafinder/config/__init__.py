# ---------------------------------------------------------------------
#
# Copyright (c) 2012 University of Oxford
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, --INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# ---------------------------------------------------------------------

import ConfigParser
import os

from django.core.exceptions import ImproperlyConfigured
from datafinder.lib.broadcast import BroadcastToRedis

class Settings(object):
    def __init__(self):
        self.config_location, self._config = self.get_config()

    def relative_to_config(self, *args):
        # Return None if any of the arguments are None.
        if all(args):
            return os.path.abspath(os.path.join(os.path.dirname(self.config_location), *args))

    @staticmethod
    def get_config():
        # Find config file
        def _config_locations():
            if 'DATAFINDER_CONFIG' in os.environ:
                yield os.environ['DATAFINDER_CONFIG']
            yield os.path.expanduser('~/.datafinder.conf')
            yield '/etc/datafinder.conf'
            yield os.path.join(os.path.dirname(__file__), 'datafinder.conf')

        for config_location in _config_locations():
            if os.path.exists(config_location):
                break
        else:
            raise ImproperlyConfigured("Couldn't find config file")

        config = ConfigParser.ConfigParser()
        config.read(config_location)

        config = dict((':'.join([sec, key]), config.get(sec, key)) for sec in config.sections() for key in config.options(sec))

        return config_location, config
    
    def __getitem__(self, key):
        return self._config[key]
    
    
    def get(self, key):
        return self._config.get(key)
    
    def getconfig(self):
        return self._config
    
    def getSolrConnection(self):
        config = self._config
        
        if config.has_key("redis.host"):
            self.redishost = config['redis.host']
            try:
                self.r = Redis(self.redishost)
            except:
                self.r = None
            if self.r and config.has_key("broadcast.to") and config['broadcast.to'] == "redis" and  config.has_key("broadcast.queue"):
                self.b = BroadcastToRedis(config['redis.host'], config['broadcast.queue'])
        else:
            self.r = None
            self.redishost = None
            self.b = None
            
        if config.has_key("main:solr.host"):
            from solr import SolrConnection
            self.solrhost = config['main:solr.host']
            try:
                self.solr = SolrConnection(self.solrhost)
            except:
                self.solr = None
        else:
            self.solrhost = None
            self.solr = None
        return self.solr,self.b

    config_item = lambda key: property(lambda self: self[key])
    SITE_NAME = config_item('main:site_name')
    SITE_VERSION = config_item('main:site_version')
    GROUP_NAME = config_item('group:name')
    GROUP_URL = config_item('group:url')
    del config_item

    @property
    def DATA_DIRECTORY(self):
        return self.relative_to_config(self._config['data:path'])

    USER_AGENT = property(lambda self:'Mozilla (compatible; DataStage/%s; %s' % (__version__, self.GROUP_URL))

settings = Settings()
