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
    def __init__(self, filter={} , cud_proxy_host=None, req_format="xml",secure=False):
        self.format = req_format
        self.secure = secure
        query = ""
        
        for key, value in filter.items():
            value = value.replace(" ", "*")
            query = query + "cud"+ "\\" + ":cas" +"\\:" + key +":"+ value + "* AND "
        
        query = query.rstrip(" AND ")

        #self.cuduri = cud_proxy_host + "/cgi-bin/querycud.py?q=cud"+ "\\" + ":cas" +"\\:"+ filter_key+":"+ filter_value +"&format=" + self.format
        self.cuduri = cud_proxy_host + "/cgi-bin/querycud.py?q=" + query +"&format=" + self.format
        logger.info(self.cuduri)
        self.xmlresponse = urllib.urlopen(self.cuduri).read()
        self.root = ET.fromstring(self.xmlresponse)       
    
    def get_xmlresponse(self):
        return  self.xmlresponse
    
    def get_ssoId(self):
        root=self.root
        ssoid = root.findtext('.//cudAttribute[name="cud:cas:sso_username"]/value')
        return ssoid 

    def get_filter_values(self, filter_key):
        logger.info('filter_key =' + filter_key)
        root=self.root
        element_list = []
        for element in root.findall('.//cudAttribute[name="cud:cas:' + filter_key + '"]/value'):
            element_list.append(element.text)
            logger.info('filter_value =' + repr(element.text) )      
        #filter_value = root.findtext('.//cudAttribute[name="cud:cas:' + filter_key + '"]/value')
        if len(element_list) == 0:
            element_list.append("");
        return element_list 
    
    def get_affiliation(self):
        root=self.root
        element_list = []
        for element in root.findall('.//cudAttribute[name="cud:cas:current_affiliation"]/value/string'):
            element_list.append(element.text)
            logger.info('filter_value =' + repr(element.text) )      
        #filter_value = root.findtext('.//cudAttribute[name="cud:cas:' + filter_key + '"]/value')
        return element_list 

    
    def get_firstName(self):
        root=self.root
        firstname = root.findtext('.//cudAttribute[name="cud:cas:firstname"]/value')
        return firstname 
    
    def get_lastName(self):
        root=self.root
        lastname = root.findtext('.//cudAttribute[name="cud:cas:lastname"]/value')
        return lastname 
    
    def get_middleName(self):
        root=self.root
        middlename = root.findtext('.//cudAttribute[name="cud:cas:middlenames"]/value')
        return middlename 
    
        
    def get_fullName(self):
        root=self.root
        fullname = root.findtext('.//cudAttribute[name="cud:cas:fullname"]/value')
        return fullname 
    
    def get_email(self):
        root=self.root
        lastname = root.findtext('.//cudAttribute[name="cud:cas:oxford_email"]/value')
        return lastname

    