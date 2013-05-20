from djangomako.shortcuts import render_to_response, render_to_string
from django.shortcuts import redirect
from django.conf import settings
from datafinder.lib.HTTP_request import HTTPRequest
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
    context={}
    try:
        # A user needs to be authenticated  to be able to view my records page in the DataFinder                          
        # Test if the user is now a university authenticated user
        if 'DF_USER_SSO_ID' not in request.session:                          
                return redirect("/login?redirectPath=myrecords")    
    
        http_method = request.environ['REQUEST_METHOD'] 
        
        if http_method == "GET":
                user_name = settings.get("main:granary.uri_root_name") 
                password = settings.get("main:granary.uri_root_pass") 
                datastore = HTTPRequest(endpointhost=settings.get("main:granary.host"))       
                datastore.setRequestUserPass(endpointuser=user_name, endpointpass=password)
                (resp,respdata) = datastore.doHTTP_GET( resource="/DataFinder/datasets/" + identifier +"/")
 
    except Exception, e:
        raise
     
    return render_to_response('myrecords.html',context, context_instance=RequestContext(request))

