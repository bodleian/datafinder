# ---------------------------------------------------------------------
#
# Copyright (c) 2012 University of Oxford
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, --INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# ---------------------------------------------------------------------

import errno
import os
import urllib
import httplib

from django.contrib.formtools.wizard import FormWizard
from django.http import Http404
from django.utils.datastructures import SortedDict
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.forms.util import ErrorList
from django.utils.datastructures import MergeDict
from django_conneg.views import HTMLView, JSONView, ErrorCatchingView
from django_conneg.http import HttpResponseSeeOther
import posix1e
from datastage.dataset.sword2depositor import Sword2, SwordSlugRejected, SwordServiceError, SwordDepositError
import datastage.util.datetime
from datastage.config import settings
from datastage.util.path import get_permissions
from datastage.util.views import RedisView
from datastage.web.dataset.models import DatasetSubmission, Repository, RepositoryUser
from datastage.web.dataset import openers, forms

from datastage.dataset import Dataset, SUBMISSION_QUEUE


import logging
v_l = logging.getLogger(__name__)

class IndexView(HTMLView):
    def get(self, request):
        dataset_submissions = DatasetSubmission.objects.all()
        if 'path' in request.GET:
            path_parts = request.GET['path'].rstrip('/').split('/')
            path_on_disk = os.path.normpath(os.path.join(settings.DATA_DIRECTORY, *path_parts))
            dataset_submissions = dataset_submissions.filter(path_on_disk=path_on_disk)
        context = {
            'dataset_submissions': dataset_submissions,
        }
        return self.render(request, context, 'dataset/index')

class SubmitView(HTMLView, RedisView, ErrorCatchingView):
    error_template_names = MergeDict({httplib.FORBIDDEN: 'dataset/403'}, ErrorCatchingView.error_template_names)
    @method_decorator(login_required)
    def dispatch(self, request):
        return super(SubmitView, self).dispatch(request)

    def common(self, request):
        path = request.REQUEST.get('path')
        num = request.REQUEST.get('num')
        reposilo = request.REQUEST.get('reposilo')
  
        if not path:
            raise Http404
        path_parts = path.rstrip('/').split('/')
        path_on_disk = os.path.normpath(os.path.join(settings.DATA_DIRECTORY, *path_parts))
        try:
            permissions = get_permissions(path_on_disk, request.user.username, check_prefixes=True)
        except IOError, e:
            if e.errno == errno.ENOENT:
                raise Http404
            elif e.errno == errno.EACCES:
                raise PermissionDenied
            raise
        if posix1e.ACL_WRITE not in permissions:
            raise  PermissionDenied

        previous_submissions = DatasetSubmission.objects.filter(path_on_disk=path_on_disk)
        
        if 'id' in request.REQUEST:
            dataset_submission = get_object_or_404(DatasetSubmission,
                                                   id=request.REQUEST['id'],
                                                   status='new',
                                                   submitting_user=request.user)
        else:
            dataset_submission = DatasetSubmission(path_on_disk=path_on_disk,
                                                   submitting_user=request.user)
                                                           
        if 'num' in request.REQUEST:           
           dataset_submission = get_object_or_404(DatasetSubmission, id=num)       
           
        form = forms.DatasetSubmissionForm(request.POST or None, instance=dataset_submission)
        
        return {'path': path,
                'num':num,
                'reposilo':reposilo,
                'form': form,
                'path_on_disk': path_on_disk,
                'previous_submissions': previous_submissions,
                'dataset_submission': dataset_submission,
                'queued': request.GET.get('queued') == 'true'}


    def get(self, request):
        context = self.common(request)
        form = context['form']
        #if context['dataset_submission'].status not in ('new', 'submitted', 'error'):
        #    return self.render(request, context, 'dataset/submitted')
        #if context['dataset_submission'].status in ('new', 'submitted', 'error'):
        #     return self.render(request, context, 'dataset/submitted')
        #opener = openers.get_opener(form.instance.repository, request.user)
        #form.instance.repository = dataset.obtain_silos(opener, repository)
        return self.render(request, context, 'dataset/submit')
    
    def post(self, request):
        context = self.common(request)
        form = context['form']
        silo = context['reposilo']
        if form.instance.status not in ('new', 'submitted', 'error'):
            return self.render(request, context, 'dataset/submitted')

        if not form.is_valid():
            return self.render(request, context, 'dataset/submit')
        
        form.save()
        dataset = form.instance.dataset

        cleaned_data = form.cleaned_data

        repository = cleaned_data['repository']
        
        redirect_url = '/dataset/submission/%s?%s' % (form.instance.id, urllib.urlencode({'path': context['path']}))

        # First thing is to try the preflight_submission

        if not context['num']:
            v_l.info("Just before try in submit view")
            try:
                opener = openers.get_opener(repository, request.user)
                v_l.info("Just before preflight submission in submitview")
                form.instance.remote_url = dataset.preflight_submission(opener, repository, silo)
                v_l.info("Just after preflight submission in submitview")
                
            except openers.SimpleCredentialsRequired:
                # FIXME: If we get this error we HAVE to save the form, so we must
                # make sure that we undo any save operation if there is an error
                # later on...
                
                form.instance.status = 'new'
                form.instance.save()  # We have to save the form or the redirect will fail, FIXME: what are we saving here?
                url = '%s?%s' % (
                    reverse('dataset:simple-credentials'),
                    urllib.urlencode({'next': '%s?%s' % (request.path, urllib.urlencode({'path': context['path'],
                                                                                         'id': form.instance.id})),
                                      'repository': repository.id}),
                )
                return HttpResponseSeeOther(url)
            except Dataset.DatasetIdentifierRejected, e:
                form.errors['identifier'] = ErrorList([unicode(e)])
                return self.render(request, context, 'dataset/submit')
            except Exception as e:
                v_l.info("General failure during submission "+repr(e))
                form.errors['repository'] = ErrorList(["Failed to connect to repository for initial deposit; please try again later"])
                return self.render(request, context, 'dataset/submit')     

          # FIXME: we probably don't want this else here, it's probably what's
          # messing things up
            
        else:
            form.instance.status = 'queued'
            form.instance.queued_at = datastage.util.datetime.now()
            form.instance.save() # FIXME: what are we saving here?

        # only save this once it has completed
        form.instance.save()  # We are saving the returned url
        self.redis.rpush(SUBMISSION_QUEUE, self.pack(form.instance.id))

    
        
        return HttpResponseSeeOther(redirect_url)

class PreviousSubmissionsView(HTMLView, RedisView, ErrorCatchingView):
    error_template_names = MergeDict({httplib.FORBIDDEN: 'dataset/403'}, ErrorCatchingView.error_template_names)
    @method_decorator(login_required)
    def dispatch(self, request):
        return super(PreviousSubmissionsView, self).dispatch(request)

    def common(self, request):
        path = request.REQUEST.get('path')
        reposilo = request.REQUEST.get('reposilo')
        if not path:
            raise Http404
        path_parts = path.rstrip('/').split('/')
        path_on_disk = os.path.normpath(os.path.join(settings.DATA_DIRECTORY, *path_parts))
        try:
            permissions = get_permissions(path_on_disk, request.user.username, check_prefixes=True)
        except IOError, e:
            if e.errno == errno.ENOENT:
                raise Http404
            elif e.errno == errno.EACCES:
                raise PermissionDenied
            raise
        if posix1e.ACL_WRITE not in permissions:
            raise  PermissionDenied

        previous_submissions = DatasetSubmission.objects.filter(path_on_disk=path_on_disk)
        
        if 'id' in request.REQUEST:
            dataset_submission = get_object_or_404(DatasetSubmission,
                                                   id=request.REQUEST['id'],
                                                   status='new',
                                                   submitting_user=request.user)
        else:
            dataset_submission = DatasetSubmission(path_on_disk=path_on_disk,
                                                   submitting_user=request.user)
                         

        form = forms.DatasetSubmissionForm(request.POST or None, instance=dataset_submission)
        
        return {'path': path,
                'form': form,
                'reposilo':reposilo,
                'path_on_disk': path_on_disk,
                'previous_submissions': previous_submissions,
                'dataset_submission': dataset_submission,
                'queued': request.GET.get('queued') == 'true'}


    def get(self, request):
        context = self.common(request)
        if context['dataset_submission'].status not in ('new', 'submitted', 'error'):
            return self.render(request, context, 'dataset/submitted')
        return self.render(request, context, 'dataset/previous-submissions')
    
    def post(self, request):
        context = self.common(request)
        form = context['form']
        silo = context['reposilo']
        if form.instance.status not in ('new', 'submitted', 'error'):
            return self.render(request, context, 'dataset/submitted')

        if not form.is_valid():
            return self.render(request, context, 'dataset/previous-submissions')
        
        form.save()
        dataset = form.instance.dataset

        cleaned_data = form.cleaned_data

        repository = cleaned_data['repository']
        
        redirect_url = '?%s' % urllib.urlencode({'path': context['path'],
                                                 'queued': 'true'})
        
        # First thing is to try the preflight_submission
                
        try:
            opener = openers.get_opener(repository, request.user)
            form.instance.remote_url = dataset.preflight_submission(opener, repository, silo)
        except openers.SimpleCredentialsRequired:
            # FIXME: If we get this error we HAVE to save the form, so we must
             # make sure that we undo any save operation if there is an error
            # later on...
                     
            form.instance.status = 'new'
            form.instance.save() # We have to save the form or the redirect will fail, FIXME: what are we saving here?
            url = '%s?%s' % (
                reverse('dataset:simple-credentials'),
                urllib.urlencode({'next': '%s?%s' % (request.path, urllib.urlencode({'path': context['path'],
                                                                                     'id': form.instance.id})),
                                  'repository': repository.id}),
            )
            return HttpResponseSeeOther(url)
        except Dataset.DatasetIdentifierRejected, e:
            form.errors['identifier'] = ErrorList([unicode(e)])
            return self.render(request, context, 'dataset/submit')
        except Exception as e:
            v_l.info("General failure during submission")
            form.errors['repository'] = ErrorList(["Failed to connect to repository for initial deposit; please try again later"])
            return self.render(request, context, 'dataset/submit')     

          # FIXME: we probably don't want this else here, it's probably what's
          # messing things up
            
        #else:
        form.instance.status = 'queued'
        form.instance.queued_at = datastage.util.datetime.now()
        form.instance.save() # FIXME: what are we saving here?

        self.redis.rpush(SUBMISSION_QUEUE, self.pack(form.instance.id))
        
        # only save this once it has completed
        # form.save()  # FIXME: what are we saving here?

        return HttpResponseSeeOther(redirect_url)


class SimpleCredentialsView(HTMLView):
    def common(self, request):
        repository = get_object_or_404(Repository, id=request.GET.get('repository'))
        repository_user, _ = RepositoryUser.objects.get_or_create(repository=repository, user=request.user)
        return {'repository': repository,
                'repository_user': repository_user,
                'form': forms.SimpleCredentialsForm(request.POST or None,
                                                    initial={'username': repository_user.username,
                                                             'next': request.REQUEST.get('next')})}

    def get(self, request):
        context = self.common(request)
        return self.render(request, context, 'dataset/simple-credentials')
    
    def post(self, request):
        context = self.common(request)
        if not context['form'].is_valid():
            return self.render(request, context, 'dataset/simple-credentials')
        
        cleaned_data = context['form'].cleaned_data
        context['repository_user'].username = cleaned_data['username']
        context['repository_user'].password = cleaned_data['password']
        context['repository_user'].save()
        
        return HttpResponseSeeOther(cleaned_data['next'])
            
            
class SilosView(HTMLView):
    #,ErrorCatchingView):
    #error_template_names = MergeDict({httplib.FORBIDDEN: 'dataset/403'}, ErrorCatchingView.error_template_names)
    @method_decorator(login_required)
    def dispatch(self, request):
        return super(SilosView, self).dispatch(request)

    def common(self, request):
        if 'path' in request.REQUEST:
            path = request.REQUEST.get('path')
        ##?path={{ path }}&num={{ num }}
        if not path:
            raise Http404
        path_parts = path.rstrip('/').split('/')
        path_on_disk = os.path.normpath(os.path.join(settings.DATA_DIRECTORY, *path_parts))
        try:
            permissions = get_permissions(path_on_disk, request.user.username, check_prefixes=True)
        except IOError, e:
            if e.errno == errno.ENOENT:
                v_l.info("2222")
                raise Http404
            elif e.errno == errno.EACCES:
                raise PermissionDenied
            raise
        if posix1e.ACL_WRITE not in permissions:
            raise  PermissionDenied

        dataset_submission = None
        if 'id' in request.REQUEST:
            dataset_submission = get_object_or_404(DatasetSubmission,
                                                   id=request.REQUEST['id'],
                                                   status='new',
                                                   submitting_user=request.user)
        else:
            dataset_submission = DatasetSubmission(path_on_disk=path_on_disk,
                                                   submitting_user=request.user)
                                                           
        if 'num' in request.REQUEST:       
           number = request.REQUEST.get('num')    
           dataset_submission = get_object_or_404(DatasetSubmission, id=number)       
           
        form = forms.DatasetSubmissionForm(request.POST or None, instance=dataset_submission)
        
        if 'num' in request.REQUEST:
           number = request.REQUEST.get('num')   
           return {'path': path,
                   'tempform': form,
                   'path': path,
                   'path_on_disk': path_on_disk,
                   'dataset_submission': dataset_submission,
                   'num': number}
        else:
            return {'path': path,
                        'tempform': form,
                        'path': path,
                        'path_on_disk': path_on_disk,
                        'dataset_submission': dataset_submission
                }
                
                
    def post(self, request):
         context = self.common(request)
         form = context['tempform']
         path = context['path']
         path_on_disk = context['path_on_disk']
         submission = context['dataset_submission']
         repo = form['repository']
         #repo = get_object_or_404(Repository, name=submission.repository.name) 
         #repo = form.repository
         #return HttpResponseSeeOther( repr(repo))
         try:
             f = open('/tmp/debug.log', 'w')
             f.write('Before repo')
             #f.write("%s, %s"%('in num, path_on_disk))
             #f.write("%s, %s"%(path_parts, path_on_disk))
             #f.write("%s, %s"%('username',  request.user.username))
             #f.write("%s, %s"%('form',  repr(form)))

             repo = get_object_or_404(Repository, id="2")
             f.write('Before get Opener')
             opener = openers.get_opener(repo, request.user)
             f.write('After get Opener')
             f.close()
             # if this is a sword2 repository, hand off the management of that to 
             # the sword2 implementation
             if repo.type == "sword2":
               v_l.info("Using SWORDv2 depositor")
               s = Sword2()
               silos = s.get_silos(opener, repo)
               v_l.info(repr(silos))
               SILO_CHOICES = []
               for silo in silos:
                    SILO_CHOICES.append(silo.title)
               SILO_CHOICES.sort()
       
               form.instance.repository = repo 
               form.instance.save()  # We have to save the form or the redirect will fail, FIXME: what are we saving here?
               if 'num' in request.REQUEST:
                  number = request.REQUEST.get('num')   
                  context ={ 'path': path,
                           'form': form,
                           'silos': SILO_CHOICES,
                           'path_on_disk': path_on_disk,
                           'dataset_submission': submission,
                           'num': number}
               else:
                  context ={'path': path,
                            'form': form,
                            'silos': SILO_CHOICES,
                            'path': path,
                            'path_on_disk': path_on_disk,
                            'dataset_submission': submission}
                        
               return self.render(request,context, 'dataset/submit')
         except SwordServiceError as e:
             raise
         except openers.SimpleCredentialsRequired:
            # FIXME: If we get this error we HAVE to save the form, so we must
            # make sure that we undo any save operation if there is an error
            # later on...
            return self.render(request,context, 'dataset/submit')
           
            
class DatasetSubmissionView(HTMLView):
    def get(self, request, id):
        path = request.REQUEST.get('path')
        dataset_submission = get_object_or_404(DatasetSubmission, id=id)
        context = {'dataset_submission': dataset_submission, 'path': path}
        return self.render(request, context, 'dataset/submission-detail')
        
    def post(self, request, id):
        path = request.REQUEST.get('path')
        context = {'path': path}
        return HttpResponseSeeOther('/data'+path)

        
#class SubmitWizard(HTMLView, JSONView, CookieWizardView):
#    pass
# Create your views here.
