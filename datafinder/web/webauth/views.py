from djangomako.shortcuts import render_to_response, render_to_string
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.conf import settings
from django.template import RequestContext
import logging,os, sys

sys.path.append("../..")
print str(sys.path)
from datafinder.lib.DF_Auth_Session import DFAuthSession
from datafinder.config import settings


logger = logging.getLogger(__name__)

def login(request):
    username = ""
    df_auth = DFAuthSession(request)
    authenticated = df_auth.isAuthenticated()
    if authenticated:
        username = request.session['DF_USER_FULL_NAME']
   
    context = { 
        #'DF_VERSION':settings.DF_VERSION,
        #'STATIC_URL': settings.STATIC_URL,
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'user_logged_in_name': username,#,
        'q':"",
        'typ':"",
        'logout':''
        }
    if request.GET.has_key('redirectPath'):
        redirectPath = request.GET.get('redirectPath')
        return HttpResponseRedirect(redirectPath)
    else:
        return render_to_response("home.html",context, context_instance=RequestContext(request))
    

def logout(request):
    context = { 
        #'DF_VERSION':settings.DF_VERSION,
        #'STATIC_URL': settings.STATIC_URL,
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'user_logged_in_name':"",
        'q':"",
        'typ':"",
        'login':''
        }

    if request.session.has_key['DF_USER_SSO_ID']:
        del request.session['DF_USER_SSO_ID']
        del request.session['DF_USER_FULL_NAME']
        del request.session['DF_USER_ROLE']
        del request.session['DF_USER_EMAIL']
    
    request.session.modified = True
    #return render_to_response('login.html',context, context_instance=RequestContext(request))
    #return render_to_response('home.html',context, context_instance=RequestContext(request))
    #return  redirect('https://webauth.ox.ac.uk/logout')
    return render_to_response("home.html",context, context_instance=RequestContext(request))