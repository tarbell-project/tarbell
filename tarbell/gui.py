# -*- coding: utf-8 -*-
"""
This module provides a web-based GUI admin for tarbell.
"""
import traceback
import os
import re
import multiprocessing
import time
import requests
from flask import Flask, request, render_template, jsonify

from tarbell import __VERSION__ as VERSION

from .admin import list_projects
from .contextmanagers import ensure_project

class TarbellAdminSite:
    def __init__(self, settings, quiet=False):
        self.settings = settings
 
        self.app = Flask(__name__)
        self.app.debug = True  # Always debug
       
        # Add routes
        self.app.add_url_rule('/', view_func=self.main)   
        self.app.add_url_rule('/settings/save/', view_func=self.settings_save)
        self.app.add_url_rule('/project/run/', view_func=self.project_run)
        self.app.add_url_rule('/project/stop/', view_func=self.project_stop)
 
    def _request_get(self, *keys):
        """Verify existence of request data and return values"""
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
 
    def _get_path(self, name):
        """Get path for project"""
        return os.path.join(self.settings.config.get('projects_path'), name)
      
    def _project_run(self, project_path, ip, port):
        with ensure_project('serve', [], path=project_path) as site:
            site.app.run(ip, port=port, use_reloader=False)
 
    def _project_stop(self):
        if self.p:
            self.p.terminate()
            self.p = None

    def main(self):
        """Main view"""
        print VERSION
        print self.settings
        print self.settings.config
        
        defaults = {
            'projects_path': os.path.expanduser(os.path.join("~", "tarbell"))
        }
        
        return render_template('admin.html', 
            version=VERSION,
            defaults=defaults,
            config=self.settings.config,
            projects=list_projects(self.settings.config.get('projects_path'))
        ) 

    def settings_save(self):
        """Save settings"""
        try:
            raise Exception('not implemented yet')
        except Exception, e:
            traceback.print_exc()
            return jsonify({'error': str(e)})
            
    def project_run(self):
        """Run preview server for project"""
        try:
            project, address = self._request_get('project', 'address')

            m = re.match(r'([\w.]+):(\d+)', address)   
            if not m:
                raise Exception('Invalid "address" parameter')

            path = self._get_path(project)
            if not os.path.exists(path):
                raise Exception('The project directory "%s" does not exist' \
                    % path)
                
            ip = m.group(1)
            port = m.group(2)
                       
            self.p = multiprocessing.Process(target=self._project_run, 
                args=(path, ip, port))
            self.p.start()
            
            # Wait for server to come up          
            for i in [1, 2, 3]:
                time.sleep(2)
                
                try:
                    print 'Waiting for server...', 'http://'+address
                    r = requests.get('http://'+address, timeout=3)
                
                    if r.status_code == requests.codes.ok:
                        return jsonify({})                       
                except requests.exceptions.ConnectionError, e:
                    print 'ERROR', e
                            
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
 
