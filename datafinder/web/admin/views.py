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
from djangomako.shortcuts import render_to_response, render_to_string
from django.conf import settings
from django.template import RequestContext
import logging, json
import sys, urllib2, base64, urllib

sys.path.append("../..")
print str(sys.path)
from datafinder.config import settings
from datafinder.lib.HTTP_request import HTTPRequest
from datafinder.lib import SparqlQueryTestCase
from datafinder.lib.conneg import MimeType as MT, parse as conneg_parse
#sys.path.append("./..")
from datafinder.web.core.models import SourceInfo


log = logging.getLogger(__name__)

def listsources(request):
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
        'message':"",
        'source_infos':{},
        'unregistered_sources':[],
        }

        src = settings.get("main:granary.uri_root")
        host = settings.get("main:granary.host")
        
        context['message']=""
        user_name = 'admin'
        password = 'test'
        #host = "192.168.2.230"
        datastore = HTTPRequest(endpointhost=host)
        datastore.setRequestUserPass(endpointuser=user_name, endpointpass=password)

        (resp, respdata) = datastore.doHTTP_GET(resource="/silos", expect_type="application/JSON")
        sources =  json.loads(respdata)
        
        source_infos ={}
        for source in sources:
            (resp, respdata) = datastore.doHTTP_GET(resource='/' + source + '/states', expect_type="application/JSON")
            state_info =  json.loads(respdata)
            source_infos[source] = [source, len(state_info['datasets'])]
        #print "sourceinfos:"
        #print source_infos
        
        context['source_infos']=source_infos

        print context
        try:
            #s_q= meta.Session.query(SourceInfo.silo).filter(SourceInfo.activate == False)
            s_q= SourceInfo.objects.filter(activate = False)
            for source in s_q:
                context['unregistered_sources'].append(source.silo)
            #print "Unregistered sources"
            #print context['unregistered_sources']
        except Exception:
            #logger.exception("Failed to mark submission as failed")
            return render_to_response('list_of_sources.html',context, context_instance=RequestContext(request))
        #print context
        return render_to_response('list_of_sources.html',context, context_instance=RequestContext(request))
 
def createsource(request):
        context = { 
            'silo_name':'',
            
            'ident':'',
            'id':"",
            'path':"",
            'user_logged_in_name':"",
            'q':"",
            'typ':"",
            'src':settings.get("main:granary.uri_root"),
            'host':settings.get("main:granary.host"),
            'silo':"",
            'source':"",
            'kw':{},       
            'activate':None,
            'message':None,
            'header':"create",
            'kw':{},
        }
        return render_to_response('create_new_source.html', context, context_instance=RequestContext(request))


def registersource(request):
        context = { 
            'silo_name':'',
            'ident':'',
            'id':"",
            'path':"",
            'user_logged_in_name':"",
            'q':"",
            'typ':"",
            'src':settings.get("main:granary.uri_root"),
            'host':settings.get("main:granary.host"),
            'message':None,
            'sourceinfo':SourceInfo(),
            #'unregistered_sources':[]
        }
        sourceinfo = SourceInfo()
        #srcurl = ag.root +'/admin'
        sourceinfo.silo = request.REQUEST.get('silo', "qwerty")
        sourceinfo.title = request.REQUEST.get('title', "")
        sourceinfo.description = request.REQUEST.get('description', "")
        sourceinfo.notes = request.REQUEST.get('notes', "")
        sourceinfo.administrators = request.REQUEST.get('administrators', "")
        sourceinfo.managers = request.REQUEST.get('managers', "")
        sourceinfo.users = request.REQUEST.get('users', "")
        sourceinfo.disk_allocation = request.REQUEST.get('disk_allocation', 0)
        context['sourceinfo'] = sourceinfo
        context['kw'] = {'silo':sourceinfo.silo, 
                            'title':sourceinfo.title,                       
                            'description':sourceinfo.description,
                            'notes':sourceinfo.notes,
                            'users':sourceinfo.users,
                            'disk_allocation':sourceinfo.disk_allocation
                           }
        try:
            #s_q= meta.Session.query(SourceInfo).filter(SourceInfo.silo == sourceinfo.silo)
            s_q= SourceInfo.objects.filter(silo = sourceinfo.silo) 
            print "s_q" + repr(len(s_q))
            #print s_q[0].silo + " " + sourceinfo.silo
            #sinfos = SourceInfo.objects.all()
            #print([p.silo for p in sinfos])
            if len(s_q) == 0:
                sourceinfo.activate =  False
                #uns_q= SourceInfo.objects.filter(activate = False)
                #for source in uns_q:
                #    context['unregistered_sources'].append(source.silo)

            else:
                context['message'] = "Source with the chosen name already exists. Choose another"
                print context['message']
                context['header']="create"
                context['activate']=None    
                return render_to_response('create_new_source.html', context, context_instance=RequestContext(request))
        except Exception, e:
            print "Exception"
            context['message'] = str(e)
            return render_to_response('create_new_source.html', context, context_instance=RequestContext(request))
            #logger.exception("Failed to mark submission as failed")
            #return render_to_response('list_of_sources.html', context, context_instance=RequestContext(request))
        #return False
        #print context
        #return render_to_response('list_of_sources.html', context, context_instance=RequestContext(request))
        #return redirect(url(controller='list_sources', action='index')) 
        return listsources(request)  
    
    
def approvesource(request,source):
        context = { 
        #'DF_VERSION':settings.DF_VERSION,
        #'STATIC_URL': settings.STATIC_URL,
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'user_logged_in_name':"",
        'q':"",
        'src':settings.get("main:granary.uri_root"),
        'host':settings.get("main:granary.host"),
        'typ':"",
        'message':"",
        'silo':"",
        'source_infos':{},
        'unregistered_sources':[],
        'kw':{},
        }

        state_info = None       
        print "source requested: "
        print source 
        context['header'] = "create"
        context['activate']=None
        context['kw']={}
        text = "Approval needed for the registered source: '" + source +"'"
       
        try:
            #s_q= meta.Session.query(SourceInfo).filter(SourceInfo.silo == c.source).filter(SourceInfo.activate == False)  
            s_q = SourceInfo.objects.filter(activate = False).filter(silo = source)
            for src in s_q:
                context['header'] = "approve"
                context['activate']=""
                context['kw'] = {'silo':src.silo, 
                        'title':src.title,                       
                        'description':src.description,
                        'notes':src.notes,
                        'administrators': src.administrators,
                        'managers':src.managers,
                        'users':src.users,
                        'disk_allocation':src.disk_allocation,
                        'activate':src.activate
                       }       
        except Exception, e:
            print "Exception"
            context['message'] = str(e)
            return createsource(request)  
    
        return render_to_response('create_new_source.html', context, context_instance=RequestContext(request))

def activatesource(request):
    
        context = { 
        #'DF_VERSION':settings.DF_VERSION,
        #'STATIC_URL': settings.STATIC_URL,
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'user_logged_in_name':"",
        'q':"",
        'src':settings.get("main:granary.uri_root"),
        'host':settings.get("main:granary.host"),
        'typ':"",
        'message':"",
        'silo':"",
        'source_infos':{},
        'header':"",
        'activate':"",
        'unregistered_sources':[],
        'kw':{},
        }

        srcurl = settings.get("main:granary.uri_root") +'/admin'
        siloN = request.REQUEST.get('silo', "")
        title = request.REQUEST.get('title', "")
        description = request.REQUEST.get('description', "")
        notes = request.REQUEST.get('notes', "")
        administrators = request.REQUEST.get('administrators', "")
        managers = request.REQUEST.get('managers', "")
        users = request.REQUEST.get('users', "")
        disk_allocation = request.REQUEST.get('disk_allocation', 0)

        user_name = 'admin'
        password = 'test'
        datastore = HTTPRequest(endpointhost=context['host'])
        
        datastore.setRequestUserPass(endpointuser=user_name, endpointpass=password)
        fields = \
            [ ("silo", siloN),
              ("title", title),
              ("description", description),
              ("notes", notes),
              ("administrators", administrators),
              ("managers", managers),
              ("users", users),
              ("disk_allocation", disk_allocation)
            ]
        print fields
        files =[]
        (reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)
        
        (resp,respdata) = datastore.doHTTP_POST(reqdata, reqtype, resource="/admin", expect_type="application/JSON")
        print 'respdata', respdata
        print 'msg', resp.msg
        print 'reason', resp.reason
        print 'status',resp.status
        print resp.read()
##            print "response data for update metadata"
        if  resp.status== 204 or resp.status==201:
            context['message'] = "Source successfully created."
            
            #Modify the source entry in the sqllite database in the data finder. Change activate = True.
            
            try:
                s_q= SourceInfo.objects.filter(silo = siloN) 
                if len(s_q) == 1:
                    sourceinfo = s_q[0]
                    sourceinfo.activate = True
                    sourceinfo.save()
                #else:   
                #   s_q.update({
                #                   'title':title,
                #                   'description':description,
                #                   'notes':notes,
                #                   'administrators':administrators,
                #                   'managers':managers,
                #                   'users':users,
                #                   'disk_allocation':disk_allocation,
                #                   'activate':True
                #                })     
                #    meta.Session.commit()
            except Exception, e:
                print "Exception"
                context['message'] = str(e)
                context['header']="approve"
                context['activate']=""    
                return render_to_response('create_new_source.html', context, context_instance=RequestContext(request))

            return listsources(request)
        else:
            context['message'] = "Source could not be successfully activated"
            context['message']  =  context['message']  + " status: " + repr(resp.status) + " " + resp.reason
            context['kw']= {   'silo':siloN, 
                        'title':title,                       
                        'description':description,
                        'notes':notes,
                        'administrators': administrators,
                        'managers':managers,
                        'users':users,
                        'disk_allocation':disk_allocation
                       }
            context['header']="approve"
            context['activate']=None    
            return render_to_response('create_new_source.html', context, context_instance=RequestContext(request))
  
  
def savesource(request):  
        print " in save source" 
        context = { 
        #'DF_VERSION':settings.DF_VERSION,
        #'STATIC_URL': settings.STATIC_URL,
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'user_logged_in_name':"",
        'q':"",
        'src':settings.get("main:granary.uri_root"),
        'host':settings.get("main:granary.host"),
        'typ':"",
        'message':"",
        'silo':"",
        'source_infos':{},
        'header':"",
        'activate':"",
        'unregistered_sources':[],
        'kw':{},
        'sourceinfo':SourceInfo(),
        }
        sourceinfo=SourceInfo()
        #srcurl = ag.root +'/admin'
        
        try:
            sourceinfo.silo = request.REQUEST.get('silo', "")
            sourceinfo.title = request.REQUEST.get('title', "")
            sourceinfo.description = request.REQUEST.get('description', "")
            sourceinfo.notes = request.REQUEST.get('notes', "")
            sourceinfo.administrators = request.REQUEST.get('administrators', "")
            sourceinfo.managers = request.REQUEST.get('managers', "")
            sourceinfo.users = request.REQUEST.get('users', "")
            sourceinfo.disk_allocation = request.REQUEST.get('disk_allocation', 0)
            sourceinfo.save()
            context['message'] = "Updates saved ..."
        except Exception, e:
            context['message'] = "Save failed !"
            return createsource(request)  
        return approvesource(request,sourceinfo.silo)


    #@rest.restrict('GET', 'POST', 'DELETE')
def sourceinfo(request, source):
        context = { 
        #'DF_VERSION':settings.DF_VERSION,
        #'STATIC_URL': settings.STATIC_URL,
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'user_logged_in_name':"",
        'q':"",
        'src':settings.get("main:granary.uri_root"),
        'host':settings.get("main:granary.host"),
        'typ':"",
        'message':"",
        'silo':"",
        'source_infos':{},
        'header':"",
        'activate':"",
        'unregistered_sources':[],
        'kw':{},
        'sourceinfo':SourceInfo(),
        'roles':[],
        'source':""
        }    
    
#        if not request.environ.get('repoze.who.identity'):
#            abort(401, "Not Authorised")
#        if not ag.granary.issilo(silo):
#            abort(404)
#        ident = request.environ.get('repoze.who.identity')
#        c.ident = ident
#        c.silo = silo
#        silos = ag.authz(ident, permission=['administrator', 'manager'])
#        if not silo in silos:
#            abort(403, "Do not have administrator or manager credentials for silo %s"%silo)
#        user_groups = list_user_groups(ident['user'].user_name)
#        if ('*', 'administrator') in user_groups:
#            #User is super user
#            c.roles = ["admin", "manager", "user"]
#        elif (silo, 'administrator') in user_groups:
#            c.roles = ["admin", "manager", "user"]
#        elif (silo, 'manager') in user_groups:
#            c.roles = ["manager", "user"]
#        else:
#            abort(403, "Do not have administrator or manager credentials for silo %s"%silo)
        http_method = request.environ['REQUEST_METHOD']
        ## hardcoded for now
        context['roles'] = ["admin", "manager", "user"]
        ##c.kw = ag.granary.describe_silo(source)
        user_name = 'admin'
        password = 'test'
        datastore = HTTPRequest(endpointhost=context['host'])
        datastore.setRequestUserPass(endpointuser=user_name, endpointpass=password)
        context['source'] = source
        state_info = None     

#        try:
#            c.kw = {    'silo':src.silo, 
#                        'title':src.title,                       
#                        'description':src.description,
#                        'notes':src.notes,
#                        'users':src.users,
#                        'disk_allocation':src.disk_allocation,
#                        'activate':src.activate
#                    }    
#            s_q= meta.Session.query(SourceInfo).filter(SourceInfo.silo == c.source).filter(SourceInfo.activate == False)  
#            s_q.one()
#            return render("/admin_sourceview.html") 
#        except orm.exc.NoResultFound:
#            sourceinfo.activate =  False
#            meta.Session.add(sourceinfo)
#            meta.Session.commit()
#            pass      
#        except IntegrityError:
#            meta.Session.rollback()
#            return False     
            
            ## If the source is not activated only then get the source information from the registered information area
        (resp, respdata) = datastore.doHTTP_GET(resource='/' + source + '/states', expect_type="application/JSON")
        state_info =  json.loads(respdata)
        ##print json.loads(respdata)
        context['kw']=state_info
        
        print "http_method = "
        print http_method
        if http_method == "GET":
            return render_to_response('admin_sourceinfo.html', context, context_instance=RequestContext(request))
        elif http_method == "POST":
            ##silo = request.REQUEST.get('silo', None)
            title = request.REQUEST.get('title', '')
            description = request.REQUEST.get('description', '')
            notes = request.REQUEST.get('notes', '')
            administrators = request.REQUEST.get('administrators', '')
            managers = request.REQUEST.get('managers', '')
            users = request.REQUEST.get('users', '')
            disk_allocation = request.REQUEST.get('disk_allocation', 0)
            fields = \
                [ ("silo", source),
                  ("title", title),
                  ("description", description),
                  ("notes", notes),
                  ("administrators", administrators),
                  ("managers", managers),
                  ("users", users),
                  ("disk_allocation", disk_allocation)
                ]
            print fields
            files =[]
            (reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)
            (resp,respdata) = datastore.doHTTP_POST(reqdata, reqtype, resource='/' + source + "/admin", expect_type="application/JSON")
            resource ='/' + source + "/admin"
            print 'respdata', respdata
            print 'msg', resp.msg
            print 'reason', resp.reason
            print 'status',resp.status
            print resp.read()
##            print "response data for update metadata"
            if  resp.status== 204  :
                context['source'] = source
                context['message'] = "Metadata updated"
                (resp, respdata) = datastore.doHTTP_GET(resource='/' + source + '/states', expect_type="application/JSON")
                state_info =  json.loads(respdata)       
                context['kw']=state_info
                print "before reloading"
                print state_info
                return render_to_response('admin_sourceinfo.html', context, context_instance=RequestContext(request))
            else:
                context['source'] = source
                context['message'] = "Metadata not updated: " + str(resp.status)
                print "metadata not updated: " + str(resp.status)
                #abort(resp.status, respdata )
                return render_to_response('admin_sourceinfo.html', context, context_instance=RequestContext(request))

                
        elif http_method == "DELETE":
            ##fields = [("silo", source)]
            ##print fields
            ##files =[]
            ##(reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)
            ##(resp,respdata) = datastore.doHTTP_DELETE(reqdata, reqtype, resource='/' + source + "/admin", expect_type="application/JSON")
          
            (resp,respdata) = datastore.doHTTP_DELETE(resource='/' + source + "/admin")
            resource ='/' + source + "/admin"
            print resp.read()
 
            print "Response Status = "
            print resp.status 

            if  resp.status== 200:
                #Modify the source entry in the sqllite database in the data finder. Change activate = False.
                try:
                    s_q = SourceInfo.objects.filter(silo = source)                                        
                    for src in s_q:
                        src.activate = False
                        src.save()
                        print "after save"
                    context['message'] = "Metadata deleted"
                except Exception, e:
                    print "Exception" +  str(e)
                    context['message'] = str(e)
            else:
                context['message'] = "Metadata could not be deleted"
                abort(resp.status, respdata )
            
            return render_to_response('list_of_sources.html', context, context_instance=RequestContext(request))

