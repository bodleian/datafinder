from djangomako.shortcuts import render_to_response, render_to_string
from django.conf import settings
from django.template import RequestContext
import logging, os

def home(request):
    context = {    
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'q':"",
        'typ':"",
       }    
    return render_to_response('home.html',context, context_instance=RequestContext(request))
 
def accessibility(request):
    context = { 
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'q':"",
        'typ':"",
        }
    return render_to_response('accessibility.html',context, context_instance=RequestContext(request))

def privacy(request):
    context = { 
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'q':"",
        'typ':"",
        }
    return render_to_response('privacy.html',context, context_instance=RequestContext(request))

def termsconditions(request):
    context = { 
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'q':"",
        'typ':"",
        }
    return render_to_response('terms-conditions.html',context, context_instance=RequestContext(request))

def about(request):
    context = { 
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'q':"",
        'typ':"",
        }
    return render_to_response('about.html',context, context_instance=RequestContext(request))

def contact(request):
    context = { 
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'q':"",
        'typ':"",
        }
    return render_to_response('contact.html',context, context_instance=RequestContext(request))

def help(request):
    context = { 
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'q':"",
        'typ':"",
        }
    return render_to_response('help.html',context, context_instance=RequestContext(request))


def cookies(request):
    context = { 
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'q':"",
        'typ':"",
        }
    return render_to_response('cookies.html',context, context_instance=RequestContext(request))

def myrecords(request):
    context = { 
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'q':"",
        'typ':"",
       }
    return render_to_response('myrecords.html',context, context_instance=RequestContext(request))

