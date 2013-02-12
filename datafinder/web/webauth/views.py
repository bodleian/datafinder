from djangomako.shortcuts import render_to_response, render_to_string
from django.shortcuts import redirect
from django.conf import settings
from django.template import RequestContext
import logging,os 

def login(request):
    user_logged_in_name = None
    if os.environ.has_key('DF_REMOTE_USER'):
        user_logged_in_name = os.environ.get('DF_REMOTE_USER')
    #user_logged_in_name = repr(os.environ)
    context = { 
        #'DF_VERSION':settings.DF_VERSION,
        #'STATIC_URL': settings.STATIC_URL,
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'user_logged_in_name': user_logged_in_name,
        'q':"",
        'typ':"",
        'logout':''
        }
    #return render_to_response('login.html',context, context_instance=RequestContext(request))
    #return  redirect('/home',context,request)
    return render_to_response('home.html',context, context_instance=RequestContext(request))

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
    #return render_to_response('login.html',context, context_instance=RequestContext(request))
    #return render_to_response('home.html',context, context_instance=RequestContext(request))
    return  redirect('https://webauth.ox.ac.uk/logout')
