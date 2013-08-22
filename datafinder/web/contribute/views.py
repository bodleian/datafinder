from djangomako.shortcuts import render_to_response, render_to_string 
from django.conf import settings
from django.shortcuts import redirect
from django.template import RequestContext
import logging,os, sys
import rdflib
from rdflib import Literal, URIRef
import datafinder.util.serializers
from datafinder.namespaces import OXDS, DCTERMS, RDF, FOAF, FUND, bind_namespaces, FUND, DOI, GEO
from pwd import  getpwnam 
sys.path.append("../..")
from django.http import HttpResponse
from datafinder.lib.DF_Auth_Session import DFAuthSession
from datafinder.config import settings
from datafinder.lib.HTTP_request import HTTPRequest
from datafinder.lib import SparqlQueryTestCase
from datafinder.lib.CUD_request import CUDRequest
import json as simplejson
import xml.etree.ElementTree as ET
import xml
from datafinder.config import settings
from datafinder.lib.broadcast import BroadcastToRedis
from datafinder.lib.SolrQuery import SolrQuery
from django.http import HttpResponseRedirect
try: 
    import simplejson as json
except ImportError: 
    import json
    
def contribute(request):
   try:
        # A user needs to be authenticated  to be able to contribute a record  the DataFinder                          
        # Test if the user is now a university authenticated user
        if 'DF_USER_SSO_ID' not in request.session:                          
            return redirect("/login?redirectPath=contribute")    
        
        context = {}
        literals = {}
        resources = {}
        project = {}
        person = {}
                
        if request.GET.has_key('message'):    
            context["message"]=request.GET['message']
        if request.GET.has_key('status'):    
            context["status"]=request.GET['status']

        http_method = request.environ['REQUEST_METHOD'] 
        
        if http_method == "GET":      
            return render_to_response('contribute.html', context, context_instance=RequestContext(request))  
        elif http_method == "POST":             
            if request.POST.has_key('record_title'):
                BASE = settings.get("main:manifest.about")
                identifier = request.POST['record_title']    
                subject = URIRef(BASE+identifier)     
                literals[DCTERMS['title']]=request.POST['record_title']
                literals[DCTERMS['alternative']]=request.POST['alt_title']
                literals[DCTERMS['description']]=request.POST['data_description']
                
                project[DCTERMS['title']]=request.POST['project_name']
                project[DCTERMS['description']]=request.POST['project_desc']
                project[DCTERMS['URI']]=request.POST['project_website']
                
                subjects = request.POST.getlist('subject_area')
                for subject in subjects:
                    literals[DCTERMS['subject']]= subject
                    
                keywords = request.POST.getlist('record_keyword')                
                for keyword in keywords:
                    literals[DCTERMS['keywords']]=keyword
                    
                literals[DCTERMS['language']]=request.POST['main_language']               
                literals[DCTERMS['status']]='Seeking Approval'
                literals[OXDS['depositor']] = request.session['DF_USER_SSO_ID']
                
                i = 1
                while True:
                     if request.GET.has_key('author_firstname_' + str(i)):                
                            person_title = request.POST['author_firstname_' + str(i)] + '-' +request.POST['author_middlename_' + str(i)] + '-' +request.POST['author_lastname_' + str(i)] 
                                              
                            person[FOAF["givenName"]]=request.POST['author_firstname_' + str(i)]
                            person[FOAF["middleName"]]=request.POST['author_middlename_' + str(i)]   
                            person[OXDS["DisplayEmail"]]=request.POST['author_middlename_check_' +  str(i)]
                            person[FOAF["familyName"]]=request.POST['author_lastname_' + str(i)]    
                            person[FOAF["mbox"]]=request.POST['author_email_' + str(i)]     
                            person[OXDS['role']]=request.POST['author_role_' + str(i)]             

                            author_member_of_oxford = request.POST['author_mof_' + str(i)]    
                            
                            if author_member_of_oxford == True:                              
                                    person[FOAF["Organization"]]=request.POST['author_institution_' + str(i)]  
                                    person[OXDS["OxfordCollege"]]=request.POST['author_oxfordcollege_'+ str(i)]           
                            else:
                                person[FOAF["Organization"]]=request.POST['author_institution_text_' + str(i)]
                            
                            people_path = settings.get("main:granary.people_path")        
                            people_manifest_filename = os.path.join(people_path, 'people.rdf')
                            people_manifest = bind_namespaces(rdflib.ConjunctiveGraph())
                            
                            try:
                                with open(people_manifest_filename, 'r') as f:
                                    people_manifest.parse(f, base=people_manifest_filename)
                            except IOError, e:
                                pass
                            
                            if people_manifest.value(FOAF[person_title], None, None) == None:
                                    people_manifest.add((FOAF[person_title], RDF.type, FOAF.Person))
                                    for key, value in person.items():
                                            people_manifest.add((FOAF[person_title], key, Literal(value)))
                                                         
                            
                            with open(people_manifest_filename, 'w') as f:
                                people_manifest.serialize(f, 'better-pretty-xml', base=people_manifest_filename)
                            os.chown(people_manifest_filename,  getpwnam('www-data').pw_uid, getpwnam('www-data').pw_gid)
                            i = i + 1
                     else:
                         break
                        
                
                #literals[OXDS['contact']] = request.POST['record_contact']
                #Save the contact details       
                person_or_role = request.POST['person_or_role'] 
                person_title=""
                if person_or_role == "is_role":
                    person_title = request.POST['record_title']
                else: 
                    person_title = request.POST['contact_firstname'] + '-' +request.POST['contact_middlename'] + '-' +request.POST['contact_lastname'] 
                    person[FOAF["givenName"]]=request.POST['contact_firstname']
                    person[FOAF["middleName"]]=request.POST['contact_middlename']   
                    person[OXDS["DisplayEmail"]]=request.POST['contact_middlename_check']
                    person[FOAF["familyName"]]=request.POST['contact_lastname'] 
                       
                person[FOAF["mbox"]]=request.POST['contact_email']     
                person[OXDS['role']]=request.POST['contact_role']   
                
                member_of_oxford = request.POST['contact_mof'] 
                if member_of_oxford == True:                            
                        person[FOAF["Organization"]]=request.POST['contact_institution']
                        person[FOAF["OxfordCollege"]]=request.POST['contact_oxfordcollege']
                else:
                    person[FOAF["Organization"]]=request.POST['contact_institution_text']
                            
                person[OXDS["Faculty"]]=request.POST['contact_faculty']          
                   
                people_path = settings.get("main:granary.people_path")        
                people_manifest_filename = os.path.join(people_path, 'people.rdf')
                people_manifest = bind_namespaces(rdflib.ConjunctiveGraph())
                            
                try:
                    with open(people_manifest_filename, 'r') as f:
                        people_manifest.parse(f, base=people_manifest_filename)
                except IOError, e:
                    pass
                            
                if people_manifest.value(FOAF[person_title], None, None) == None:
                        people_manifest.add((FOAF[person_title], RDF.type, FOAF.Person))
                        for key, value in person.items():
                                people_manifest.add((FOAF[person_title], key, Literal(value)))
                                                         
                            
                with open(people_manifest_filename, 'w') as f:
                    people_manifest.serialize(f, 'better-pretty-xml', base=people_manifest_filename)
                os.chown(people_manifest_filename,  getpwnam('www-data').pw_uid, getpwnam('www-data').pw_gid)      
                
                #end of saving contact details
                
                          
                #literals[OXDS['isEmbargoed']] = 'False'
                if request.POST.has_key('data-format'):
                    literals[OXDS['isDigital']]=request.POST['data-format']
                
                literals[OXDS['DataLocation']]=request.POST['data_location']
                
                if request.POST['loc-format'] =="URL":
                    resources[DCTERMS['Location']]=request.POST['geo_location']
                else:
                    literals[DCTERMS['Location']]=request.POST['geo_location']
                    
                if request.POST['temporal_choice'] == 'single_date':
                    literals[OXDS['dataTemporalCoverage']]=request.POST['single_temporal_date']
                if request.POST['temporal_choice'] == 'date_range':
                    literals[OXDS['dataCoverageStart']]=request.POST['start_date_range']
                    literals[OXDS['dataCoverageEnd']]=request.POST['end_date_range']
                    
                if request.POST['data_collected_temporal_choice'] == 'single_date':
                    literals[OXDS['dataCollectedCoverage']]=request.POST['data_collected_single_temporal_date']
                if request.POST['data_collected_temporal_choice'] == 'date_range':
                    literals[OXDS['dataCollectedStart']]=request.POST['data_collected_start_date_range']
                    literals[OXDS['dataCollectedEnd']]=request.POST['data_collected_end_date_range']
                
                literals[GEO['lat']]=request.POST['lat']
                literals[GEO['lng']]=request.POST['lng']
                
                
                if request.POST['doc-format'] =="URL":
                    resources[OXDS['methodology']]=request.POST['digital_publisher_doc']
                else:
                    literals[OXDS['methodology']]=request.POST['digital_publisher_doc']
                    
                literals[DCTERMS['publisher']]=request.POST['publisher']
                literals[DCTERMS['issued']]=request.POST['publication_year']

               
                if literals[OXDS['isDigital']] == "yes":
                    literals[DOI['doi']]=request.POST['digital_object_identifier']  
                    literals[DCTERMS['type']]=request.POST['digital_resource_type']      
                    literals[OXDS['Filesize']]=request.POST['digital_filesize']
                    literals[DCTERMS['format']]=request.POST['digital_format']
                    literals[OXDS['currentversion']]=request.POST['digital_version']
                                       

                funded_research = request.POST['funded_research']
                if funded_research == "yes":
                    funding_agencies = request.POST.getlist('funding_agency')                
                    for funding_agency in funding_agencies:
                        literals[FUND['FundingBody']]=funding_agency
                        
                    grant_numbers = request.POST.getlist('grant_number')                
                    for grant_number in grant_numbers:
                        literals[FUND['grantNumber']]=grant_number

                #    
                #if request.POST['dmp_loc'] =="URL":
                #    resources[OXDS['data_management_plan_location']]=request.POST['data_management_plan_location']
                #else:
                #    literals[OXDS['data_management_plan_location']]=request.POST['data_management_plan_location']     
 
                
                #context["publication_relationship_of_data_1"]=request.GET['publication_relationship_of_data_1']
                #context["related_publication_url_1"]=request.GET['related_publication_url_1']
                #context["dataset_relationship_of_data_1"]=request.GET['dataset_relationship_of_data_1']
                #context["dataset_related_url_1"]=request.GET['dataset_related_url_1']
                #context["deposit_data_file_upload"]=request.POST['deposit_data_file_upload']
                #context["deposit_data_embargo_options"]=request.POST['deposit_data_embargo_options']
                #context["deposit_data_embrago_release_date"]=request.POST['deposit_data_embrago_release_date']
                #context["deposit_data_embargo_options_type"]=request.POST['deposit_data_embargo_options_type']
                #context["deposit_data_embargo_reason"]=request.POST['deposit_data_embargo_reason']
                
                literals[DCTERMS['rights']]=request.POST['terms_and_conditions']
                #resources[OXDS['DataLocation']]=request.POST['data_location']
                
                            #prepared_licence - urls to licenses stored elsewhere
                            #select_a_licence - urls of licens selted fromt he select dropdown
                            #bespoke_licence - license pasted in as free text
                            #other_licence - eg: none ie. when not associated with any license               
                license = request.POST['license_radio']
                if license =="prepared_licence" or license == 'select_a_licence':
                    resources[DCTERMS['license']]=request.POST['data_standard_licence_URI']
                else :
                    literals[DCTERMS['license']]=request.POST['data_standard_licence_text']
                    
                
                embargo_options = request.POST['embargo_options']
                # embargo_options_list = ['embargo_status_unknown','embargoed_indefinitely']
                
                
                literals[OXDS['lastaccessdate']]=request.POST['embargo_end_date']
                
                
                #context["embargo-options"]=request.GET['embargo-options']
                #context["subject_specific_metadata_file"]=request.GET['subject_specific_metadata_file']
                #context["xml_schema_type"]=request.GET['xml_schema_type']
                
                # Project RDF
                #projects_package = rdflib.URIRef(projects_path)
                
                
                projects_path = settings.get("main:granary.projects_path")        
                projects_manifest_filename = os.path.join(projects_path, 'projects.rdf')
                projects_manifest = bind_namespaces(rdflib.ConjunctiveGraph())
#              
                try:
                    with open(projects_manifest_filename, 'r') as f:
                        projects_manifest.parse(f, base=projects_manifest_filename)
                except IOError, e:
                    pass
                
                
                for key, value in project.items():
                    # Will raise UniquenessError if >1 value returned, must be one or None
                    if projects_manifest.value(None, DCTERMS['title'], Literal(value)) == None:                        
                        projects_manifest.add((FUND[project[DCTERMS['title']]], key, Literal(value)))
                    
                with open(projects_manifest_filename, 'w') as f:
                    projects_manifest.serialize(f, 'better-pretty-xml', base=projects_manifest_filename)
                os.chown(projects_manifest_filename,  getpwnam('www-data').pw_uid, getpwnam('www-data').pw_gid)
                resources[FUND['project']] = FUND[project[DCTERMS['title']]]
                
                # Record Manifest RDF
                records_path = settings.get("main:granary.records_path")
                records_package = rdflib.URIRef(records_path)
                #manifest_name = 'df_manifest_'+literals[DCTERMS['title']] +'.rdf'
                df_manifest_name = 'df_manifest.rdf'
                manifest_filename = os.path.join(records_path, df_manifest_name)
                main_manifest_filename = os.path.join(records_path, 'manifest.rdf')
                manifest = bind_namespaces(rdflib.ConjunctiveGraph())
                #try:
                #    with open(manifest_filename, 'w') as f:
                #        manifest.parse(f, base=manifest_filename)
                #except IOError, e:
                #    pass
                
                #for x in list(literals.keys()):
                #    if literals[x] == "":
                #        del literals[x]
                
                for key, value in literals.items():
                    manifest.add((subject, key, Literal(value)))
                
                for key, res_uri in resources.items():
                    manifest.add((subject, key, res_uri))
                    
                with open(manifest_filename, 'w') as f:
                    manifest.serialize(f, 'better-pretty-xml', base=manifest_filename)
                                
#                try:
#                    with open(main_manifest_filename, 'w') as f:
#                        manifest.parse(f, base=main_manifest_filename)
               
#                except IOError, e:
#                    pass
                                
                user_name = settings.get("main:granary.uri_root_name") 
                password = settings.get("main:granary.uri_root_pass") 
                datastore = HTTPRequest(endpointhost=settings.get("main:granary.host"))       
                datastore.setRequestUserPass(endpointuser=user_name, endpointpass=password)
             
                #(reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata([], [])
                # Create a dataset
                #(resp,respdata) = datastore.doHTTP_POST(reqdata, reqtype, resource="/DataFinder/datasets/" + identifier)

                #Submit the df_manefest as a file
                fields=[]
                df_namifest = open(manifest_filename).read()               
                files =  [("file", df_manifest_name, df_namifest, "application/rdf+xml")]            
                (reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)                
                (resp,respdata) = datastore.doHTTP_POST(reqdata, reqtype, resource="/DataFinder/datasets/" + identifier +"/")
                
                silo = settings.get("main:mainsilo")
                #solr_conn, b = settings.getSolrConnection()
                b = BroadcastToRedis('localhost', 'silochanges')
                b.creation(silo, identifier, ident=request.session['DF_USER_SSO_ID'])
                
                #Submit the main manifest file which as the see also
                fields=[]       

                main_manifest = open(main_manifest_filename).read()
                files =  [("file", "manifest.rdf", main_manifest, "application/rdf+xml")]            
                (reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)                
                (resp,respdata) = datastore.doHTTP_POST(reqdata, reqtype, resource="/DataFinder/datasets/" + identifier +"/")

                os.chown(manifest_filename, getpwnam('www-data').pw_uid, getpwnam('www-data').pw_gid)
                return render_to_response('contribute.html', context, context_instance=RequestContext(request))                                       
   except Exception, e:
        raise
    

def projects(request):
   try:
        # A user needs to be authenticated  to be able to contribute a record  the DataFinder                          
        # Test if the user is now a university authenticated user
        if 'DF_USER_SSO_ID' not in request.session:                          
            return redirect("/login?redirectPath=contribute")    
        
        #context = {}
        projects = {}

       
        projects_path = settings.get("main:granary.projects_path")
        
        projects_manifest_filename = os.path.join(projects_path, 'projects.rdf')
        projects_manifest = bind_namespaces(rdflib.ConjunctiveGraph())
#              
        try:
            with open(projects_manifest_filename, 'r') as f:
                projects_manifest.parse(f, base=projects_manifest_filename)
        except IOError, e:
            pass
                
        #if request.GET.has_key('message'):    
        #    context["message"]=request.GET['message']
        #if request.GET.has_key('status'):    
        #    context["status"]=request.GET['status']

        http_method = request.environ['REQUEST_METHOD'] 
        
        if http_method == "POST" or http_method == "GET":     
   #projects[o1] =projects_manifest.value(s1,DCTERMS['URI'],None)
            projects = {}
            for s1,p1,o1 in projects_manifest.triples((None,DCTERMS['title'],None)):
                     projects[o1] = {}
                     for s2,p2,o2 in projects_manifest.triples((s1,DCTERMS['description'],None)):
                                       projects[o1]['desc'] = o2
                                       #projects.append(o1)
                     for s2,p2,o3 in projects_manifest.triples((s1,DCTERMS['URI'],None)):
                                       projects[o1]['website'] = o3
                                       #projects.append(o1)
                                       

                                       

            #context['projects'] = projects
            
       
            return HttpResponse(json.dumps(projects), mimetype="application/json")
            #return render_to_response('contribute.html', context, context_instance=RequestContext(request))  
       # elif http_method == "POST":             
       #     return render_to_response('contribute.html', context, context_instance=RequestContext(request))                                       
   except Exception, e:
        raise
    

def languages(request):
   try:
        # A user needs to be authenticated  to be able to contribute a record  the DataFinder                          
        # Test if the user is now a university authenticated user
        if 'DF_USER_SSO_ID' not in request.session:                          
            return redirect("/login?redirectPath=contribute")    
        
        #context = {}
        languages = []
        tmp=[]
        languages_xml_file_path = settings.get("main:granary.languages_path")
        
        languages_xml_filename = os.path.join(languages_xml_file_path, 'languages-iso-639.xml')
      
        tree = ET.parse(languages_xml_filename)
        for elem in tree.iter():
            if request.GET['lang'].lower() in elem.text.lower():
                if elem.text[:len(request.GET['lang'])].lower() == request.GET['lang'].lower() :
                    languages.append(elem.text)
                else:
                    tmp.append(elem.text)
        languages.sort();
        tmp.sort();

        languages = languages + tmp;
        
        return HttpResponse(json.dumps(languages), mimetype="application/json")
            #return render_to_response('contribute.html', context, context_instance=RequestContext(request))  
       # elif http_method == "POST":             
       #     return render_to_response('contribute.html', context, context_instance=RequestContext(request))                                       
   except Exception, e:
        raise
        
        
def peopleFromCUD(request):
   try:
        # A user needs to be authenticated  to be able to contribute a record  the DataFinder                          
        # Test if the user is now a university authenticated user
        if 'DF_USER_SSO_ID' not in request.session:                          
            return redirect("/login?redirectPath=contribute")    

        http_method = request.environ['REQUEST_METHOD'] 
        context = {}
        if http_method == "POST":
            cud_authenticator = settings.get('main:cud_proxy.host')
            data_filter = {}
            if request.POST.has_key('lastname') and request.POST['lastname'] != "": 
                data_filter['lastname']= request.POST['lastname']
            if request.POST.has_key('firstname') and request.POST['firstname'] != "":
                data_filter['firstname']= request.POST['firstname']
            if request.POST.has_key('middlename') and request.POST['middlename'] != "":
                data_filter['middlename']= request.POST['middlename']
            if request.POST.has_key('email') and request.POST['email'] != "":
                data_filter['oxford_email']= request.POST['email']

            cudReq = CUDRequest(cud_proxy_host=cud_authenticator,filter=data_filter)
            

            context["firstname"]  =  sorted(set(cudReq.get_filter_values('firstname')))
            #str(cudReq.get_filter_values('sso_username'))
            context["lastname"]  = sorted(set(cudReq.get_filter_values('lastname')))
            context["middlename"]  = sorted(set(cudReq.get_filter_values('middlenames')))
            context["email"]  = sorted(set(cudReq.get_filter_values('oxford_email')))            
            context["affiliation"]  =  sorted(set(cudReq.get_affiliation())) #cudReq.get_affiliation()#sorted(set(cudReq.get_affiliation()))

        return HttpResponse(json.dumps(context), mimetype="application/json")
            #return render_to_response('contribute.html', context, context_instance=RequestContext(request))  
       # elif http_method == "POST":             
       #     return render_to_response('contribute.html', context, context_instance=RequestContext(request))                                       
   except Exception, e:
        raise
        

    
