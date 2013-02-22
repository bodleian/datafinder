from djangomako.shortcuts import render_to_response, render_to_string 
from django.conf import settings
from django.shortcuts import redirect
from django.template import RequestContext
import logging,os, sys

sys.path.append("../..")

from datafinder.lib.DF_Auth_Session import DFAuthSession
from datafinder.config import settings

def contribute(request):
   try:
    # A user need to be webauth-ed  to be able to contribute a record to the DataFinder
    if  request.session.has_key('DF_USER_SSO_ID'):    
        username = request.session['DF_USER_FULL_NAME']       
        context = { 
            #'DF_VERSION':settings.DF_VERSION,
            #'STATIC_URL': settings.STATIC_URL,
            'silo_name':"",
            'ident' : "",
            'id':"",
            'path' :"",
            'user_logged_in_name':username,
            'q':"",
            'typ':"",
            'message':None,
            'silo':"",
            'source':" ",
            'kw':{},       
            'activate' : None,
            'message':None,
            'header':"create",
            'kw':{},      
            }
        return render_to_response('contribute.html', context, context_instance=RequestContext(request))   
    else:     
        return redirect("/login?redirectPath=contribute")
   except Exception, e:
        raise
        #return render_to_response('contribute.html', context, context_instance=RequestContext(request))
    #return render_to_response('home.html',context, context_instance=RequestContext(request))
#    'src' : ag.root,
#        'host' : ag.host,
#        'silo':"",
#        'source' : "",
#        'kw':{},       
#        'activate' : None,
#        'message':None,
#        'header':"create",
#        'kw':{}