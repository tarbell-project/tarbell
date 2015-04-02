# -*- coding: utf-8 -*-
"""
This module provides a web-based GUI admin for tarbell.
"""
import copy
import os
import re
import multiprocessing
import time
import traceback
import requests
import json
from flask import Flask, request, render_template, jsonify

from tarbell import __VERSION__ as VERSION

from .admin import DEFAULT_BLUEPRINTS, props, safe_write, \
    get_or_create_config, list_projects, \
    client_secrets_authorize_url, client_secrets_authorize
from .contextmanagers import ensure_project
from .settings import Settings


class TarbellAdminSite:
    def __init__(self, quiet=False): 
        self.app = Flask(__name__)
        self.app.debug = True  # Always debug

        # Default settings
        self.defaults = {
            'default_s3_access_key_id': '',
            'default_s3_secret_access_key': '',
            'default_s3_buckets': {},
            'google_account': '',
            'project_templates': copy.deepcopy(DEFAULT_BLUEPRINTS),
            'projects_path': os.path.expanduser(
                os.path.join("~", "tarbell")),
            's3_credentials': {}
        }

        # Add routes
        self.app.add_url_rule('/', view_func=self.main)   
        
        self.app.add_url_rule('/projects/list/',
             view_func=self.projects_list)
             
        self.app.add_url_rule('/google/auth/secrets/',
            view_func=self.google_auth_secrets, methods=['POST'])
        self.app.add_url_rule('/google/auth/url/',
            view_func=self.google_auth_url)
        self.app.add_url_rule('/google/auth/code/',
            view_func=self.google_auth_code)
                                        
        self.app.add_url_rule('/config/save/',
            view_func=self.config_save, methods=['POST'])
            
        self.app.add_url_rule('/project/run/', 
            view_func=self.project_run)
        self.app.add_url_rule('/project/stop/', 
            view_func=self.project_stop)
 
    def _request_get(self, *keys):
        """Get request data"""
        if request.method == 'POST':
            obj = request.form
        else:
            obj = request.args
        values = []
        for k in keys:
            v = obj.get(k, '')
            values.append(v)
        if len(values) > 1:
            return values
        return values[0]

    def _request_get_required(self, *keys):
        """Get required request data"""
        if request.method == 'POST':
            obj = request.form
        else:
            obj = request.args
        values = []
        for k in keys:
            v = obj.get(k)
            if not v:
                raise Exception('Expected "%s" parameter' % k)
            values.append(v)
        if len(values) > 1:
            return values
        return values[0]
 
    def _client_secrets_path(self):
        """Get path for client_secrets"""
        return os.path.join(
            os.path.dirname(self.settings.path), "client_secrets.json")     
          
    def _project_path(self, name):
        """Get path for project"""
        return os.path.join(
            self.settings.config.get('projects_path'), name)
      
    def _project_run(self, project_path, ip, port):
        with ensure_project('serve', [], path=project_path) as site:
            site.app.run(ip, port=port, use_reloader=False)
 
    def _project_stop(self):
        if self.p:
            self.p.terminate()
            self.p = None

    def main(self):
        """Main view"""
        self.settings = Settings()
        
        projects = []
        
        if self.settings.file_missing:
            get_or_create_config(self.settings.path)
            
            for key, value in self.defaults.iteritems():
                self.settings.config[key] = copy.deepcopy(value)            
        else:
            projects = list_projects(
                self.settings.config.get('projects_path'))   
        
        return render_template('admin.html', 
            version=VERSION,
            defaults=self.defaults,
            settings=props(self.settings),
            projects=projects
        ) 
    
    def projects_list(self):
        """Get a list of projects"""
        try:
            projects = list_projects(
                self.settings.config.get('projects_path'))   
            return jsonify({'projects': projects})
        except Exception, e:
            traceback.print_exc()
            return jsonify({'error': str(e)})
            
    def google_auth_secrets(self):
        """Copy client_secrets to settings directory"""
        try:
            content = self._request_get_required('content')
       
            m = re.match('data:(.+);base64,(.+)', content)
            if not m:
                raise Exception('Expected content as data-url')
           
            content_type = m.group(1)
            content = m.group(2).decode('base64')
            print content                               # DEBUG
            
            client_secrets_path = self._get_client_secrets_path()
            print 'Writing %s' % client_secrets_path    # DEBUG
            safe_write(content, client_secrets_path)

            self.settings = Settings()  # reload settings
            
            return jsonify({'settings': props(self.settings)})
        except Exception, e:
            traceback.print_exc()
            return jsonify({'error': str(e)})
    
    def google_auth_url(self):
        """Get google authorization url"""
        try:
            url = client_secrets_authorize_url(
                self.settings.client_secrets_path)
            
            return(jsonify({'url': url}))
        except Exception, e:
            traceback.print_exc()
            return jsonify({'error': str(e)})
    
    def google_auth_code(self):
        """Verify google confirmation code"""
        try:
            code = self._request_get_required('code')                       
            client_secrets_authorize(
                self.settings.client_secrets_path, code)            
            
            return jsonify({})
        except Exception, e:
            traceback.print_exc()
            return jsonify({'error': str(e)})
 
    def config_save(self):
        """Save the configuration"""
        try:           
            config = json.loads(self._request_get_required('config'))
            
            projects_path = os.path.abspath(config.get('projects_path', 
                self.defaults.get('projects_path', '')))             
            if not os.path.isdir(projects_path):
                os.makedirs(projects_path)
           
            self.settings.config = config
            self.settings.save()
            
            return jsonify({})
        except Exception, e:
            traceback.print_exc()
            return jsonify({'error': str(e)})
                                
    def project_run(self):
        """Run preview server for project"""
        try:
            project, address = self._request_get_required(
                'project', 'address')

            m = re.match(r'([\w.]+):(\d+)', address)   
            if not m:
                raise Exception('Invalid "address" parameter')

            path = self._project_path(project)
            if not os.path.exists(path):
                raise Exception(
                    'The project directory "%s" does not exist' % path)
                
            ip = m.group(1)
            port = m.group(2)
                       
            self.p = multiprocessing.Process(target=self._project_run, 
                args=(path, ip, port))
            self.p.start()
            
            # Wait for server to come up  
            r = None        
            for i in [1, 2, 3]:
                time.sleep(2)
                
                try:
                    print 'Waiting for server @ http://%s' % address
                    r = requests.get('http://'+address, timeout=3)
                
                    if r.status_code == requests.codes.ok:
                        return jsonify({})       
                except requests.exceptions.ConnectionError, e:
                    # If the server isn't running at all...
                    print 'ERROR', e    
            
            if r is not None:
                return jsonify({'warning': \
                    'Started preview server with error (%d)' \
                        % r.status_code}) 
            
            raise Exception('Could not start preview server')
        except Exception, e:
            traceback.print_exc()
            return jsonify({'error': str(e)})
            
    def project_stop(self):
        """Stop preview server"""
        try:
            self._project_stop()
            return jsonify({})
        except Exception, e:
            traceback.print_exc()
            return jsonify({'error': str(e)})
 
