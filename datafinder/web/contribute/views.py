from djangomako.shortcuts import render_to_response, render_to_string 
from django.conf import settings
from django.template import RequestContext
import logging

def contribute(request):
    c = {}
    
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
        'message':None,
        'silo':"",
        'source':" ",
        'kw':{},       
        'activate' : None,
        'message':None,
        'header':"create",
        'kw':{},      
        }
    return render_to_response('contribute.html',context, context_instance=RequestContext(request))
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