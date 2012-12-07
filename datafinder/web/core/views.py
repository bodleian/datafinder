from djangomako.shortcuts import render_to_response, render_to_string
from django.conf import settings
from django.template import RequestContext
import logging

def home(request):
    context = { 
        #'DF_VERSION':settings.DF_VERSION,
        #'STATIC_URL': settings.STATIC_URL,3
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'user_logged_in_name':"",
        'q':"",
        'typ':"",
        }
    return render_to_response('home.html',context, context_instance=RequestContext(request))
    #return render_to_response('home.html',context, context_instance=RequestContext(request))
    
    
        #return render_to_response('home.html',context, context_instance=RequestContext(request))

def accessibility(request):
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
        }
    return render_to_response('accessibility.html',context, context_instance=RequestContext(request))

def privacy(request):
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
        }
    return render_to_response('privacy.html',context, context_instance=RequestContext(request))

def termsconditions(request):
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
        }
    return render_to_response('terms-conditions.html',context, context_instance=RequestContext(request))

def about(request):
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
        }
    return render_to_response('about.html',context, context_instance=RequestContext(request))

def contact(request):
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
        }
    return render_to_response('contact.html',context, context_instance=RequestContext(request))

def help(request):
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
        }
    return render_to_response('help.html',context, context_instance=RequestContext(request))


def cookies(request):
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
        }
    return render_to_response('cookies.html',context, context_instance=RequestContext(request))
