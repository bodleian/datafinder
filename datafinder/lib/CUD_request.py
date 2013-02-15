# -*- coding: utf-8 -*-
"""
Copyright (c) 2012 University of Oxford

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, --INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging
import mimetypes
import httplib,urllib
import base64
import urlparse
import json as simplejson
import xml.etree.ElementTree as ET
#from elementtree.ElementTree import ElementTree


logger = logging.getLogger('CUD Request')

class CUDRequest():
    def __init__(self, cud_proxy_host=None,  sso_id=None, req_format="xml",secure=False):
        self.sso_username = sso_id
        self.format = req_format
        self.secure = secure
        self.cuduri = cud_proxy_host + "/cgi-bin/querycud.py?q=cud"+ "\\" + ":cas" +"\\"+":sso_username:" + self.sso_username +"&format=" + self.format
        self.xmlresponse = urllib.urlopen(self.cuduri).read()
        self.root = ET.fromstring(self.xmlresponse)


    def get_xmlresponse(self):
        return  self.xmlresponse
    
    def get_fullName(self):
        root=self.root
        fullname = root.findtext('.//cudAttribute[name="cud:cas:fullname"]/value')
        return fullname 

    def get_firstName(self):
        root=self.root
        firstname = root.findtext('.//cudAttribute[name="cud:cas:firstname"]/value')
        return firstname 
    
    def get_lastName(self):
        root=self.root
        lastname = root.findtext('.//cudAttribute[name="cud:cas:lastname"]/value')
        return lastname 
    
    def get_email(self):
        root=self.root
        lastname = root.findtext('.//cudAttribute[name="cud:cas:oxford_email"]/value')
        return lastname

    