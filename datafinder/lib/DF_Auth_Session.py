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

import logging, os
from django.conf import settings
from datafinder.lib.CUD_request import CUDRequest
from datafinder.web.core.models import Users
from datafinder.config import settings
from datafinder.web.core.models import DFSessions

logger = logging.getLogger('DF Auth')

class DFAuthSession():
    def __init__(self, request=None):
        # Only do webauth and issue cud-requests if the session variable not found      
        if not request.session.has_key('DF_USER_SSO_ID'):        
            user_logged_in_name = None
            df_user_sso_id = None
            
            if os.environ.has_key('DF_REMOTE_USER'):
                df_user_sso_id = os.environ.get('DF_REMOTE_USER')
                
            cud_authenticator = settings.get('main:cud_proxy.host')
            cudReq = CUDRequest(cud_proxy_host=cud_authenticator,filter= {'sso_username':df_user_sso_id})
            
            user_logged_in_name = str(cudReq.get_fullName())
            user_email = str(cudReq.get_email())
            
            if not request.session.exists(request.session.session_key):
                        request.session.create()
        #set up the session variables
            request.session['DF_USER_SSO_ID'] = df_user_sso_id
            request.session['DF_USER_FULL_NAME'] = user_logged_in_name
            request.session['DF_USER_EMAIL'] = user_email
            
        #Add the user to the database if already not registered
            try:
                users = Users.objects.filter(sso_id=df_user_sso_id)
                if len(users) == 0:
                    request.session['DF_USER_ROLE'] = "user"
                    newuser = Users()
                    newuser.sso_id = request.session['DF_USER_SSO_ID']
                    newuser.username = request.session['DF_USER_FULL_NAME']
                    newuser.role = request.session['DF_USER_ROLE']
                    newuser.email = request.session['DF_USER_EMAIL']
                    newuser.save()
                else:
                    for user in users:
                        request.session['DF_USER_ROLE'] = user.role           
            except Exception:
               self.authenticated=False           
            
            request.session.modified = True
             # Save the session key in DFSessions
            try:
                    usersession= DFSessions.objects.get(session_id=request.session.session_key)                      
                    #usersession.session_id = request.session.session_key
                    #usersession.save()
            except DFSessions.DoesNotExist,e:
                    usersession =  DFSessions()
                    usersession.sso_id= request.session['DF_USER_SSO_ID']
                    usersession.session_id = request.session.session_key
                    usersession.save()
            except Exception,e:
                    logger.error("User session could not be saved in DF.")
        
        request.session.modified = True
        self.authenticated=True


    def isAuthenticated(self):
        return  self.authenticated
    