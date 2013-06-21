from djangomako.shortcuts import render_to_response, render_to_string
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.conf import settings
from django.template import RequestContext
import logging,os, sys
from datafinder.web.core.models import DFSessions
from datafinder.lib.CUD_request import CUDRequest
sys.path.append("../..")
print str(sys.path)
from datafinder.lib.DF_Auth_Session import DFAuthSession
from datafinder.config import settings

logger = logging.getLogger(__name__)

def login(request):

    df_auth = DFAuthSession(request)
    authenticated = df_auth.isAuthenticated()
       
    if authenticated and request.GET.has_key('redirectPath'):
        redirectPath = request.GET.get('redirectPath')
        return HttpResponseRedirect(redirectPath)
    else:
        return HttpResponseRedirect('home')
    

def logout(request):
    if request.session.has_key('DF_USER_SSO_ID'):
        try:
            usersession= DFSessions.objects.get(sso_id=request.session['DF_USER_SSO_ID'])                      
            usersession.delete()
        except DFSessions.DoesNotExist,e:
            pass
        except Exception,e:
            logger.error("Error while deleting the DF User session")        
    
        del request.session['DF_USER_SSO_ID']
        del request.session['DF_USER_FULL_NAME']
        del request.session['DF_USER_ROLE']
        del request.session['DF_USER_EMAIL']
        request.session.modified = True
        
    return HttpResponseRedirect('home')
    #return render_to_response("home.html",context, context_instance=RequestContext(request))