from flask import Flask, render_template, request, send_from_directory, Response
import time
import os
from jinja2 import Markup, PrefixLoader, FileSystemLoader, ChoiceLoader
from ordereddict import OrderedDict
from gdata.spreadsheet.service import SpreadsheetsService
from gdata.spreadsheet.service import CellQuery
import json
import imp
import shutil
import codecs
from slughifi import slughifi
import mimetypes

def silent_none(value):
    if value is None:
        return ''
    return value


class TarbellSite:
    def __init__(self, projects_path):
        self.app = Flask(__name__)

        self.app.jinja_env.finalize = silent_none  # Don't print "None"
        self.app.debug = True  # Always debug

        self.projects_path = projects_path
        self.projects = self.load_projects()
        self.project = self.projects[0][1]

        self.spreadsheet_data = {}
        self.expires = 0

        self.app.add_url_rule('/', view_func=self.preview)
        self.app.add_url_rule('/<path:path>', view_func=self.preview)
        self.app.add_template_filter(slughifi, 'slugify')

    def filter_projects(self):
        for dirpath, dirnames, filenames in os.walk(self.projects_path):
            dirnames[:] = [
                dn for dn in dirnames
                if not dn.startswith('.') and not dn.startswith('_') 
                ]
            yield dirpath, dirnames, filenames

    def sort_modules(self, x, y):
        if x[0] == "base": return 1
        return -1

    def load_projects(self):
        projects = []
        for root, dirs, files in self.filter_projects():
            if 'config.py' in files:
                name = root.split('/')[-1]
                filename, pathname, description = imp.find_module('config', [root])
                project = imp.load_module(name, filename, pathname, description)
                projects.append((name, project, root))

        # Sort modules
        projects = sorted(projects, cmp=self.sort_modules)

        loaders = []
        for name, project, root in projects:

            try:
                project.CREATE_JSON
            except AttributeError:
                project.CREATE_JSON = True

            try:
                project.DEFAULT_CONTEXT
            except AttributeError:
                project.DEFAULT_CONTEXT = {}

            ## Register as flask blueprint
            try:
                self.app.register_blueprint(project.blueprint)
            except AttributeError:
                pass

            ## Every directory is a template dir
            loader = FileSystemLoader(root)
            loaders.append(loader)

        self.app.jinja_loader = ChoiceLoader(loaders)

        return projects


    def preview(self, path=None):
        """ Preview a project path """
        if path is None:
            path = 'index.html'
        if path.endswith('/'):
            path += 'index.html'

        ## Serve JSON
        if path == 'data.json':
            context = self.get_context_from_gdoc()
            return Response(json.dumps(context), mimetype="application/json")

        ## Detect files
        filepath = None
        for name, project, root in self.projects:
            fullpath = os.path.join(root, path)
            try:
                with open(fullpath) as file:
                    mimetype, encoding = mimetypes.guess_type(fullpath)
                    filepath = fullpath
            except IOError: pass

        if filepath and mimetype and mimetype.startswith("text/"):
            context = self.project.DEFAULT_CONTEXT
            context.update(self.get_context_from_gdoc())
            rendered = render_template(path, **context)
            return Response(rendered, mimetype=mimetype)
        elif filepath:
            dir, filename = os.path.split(filepath)
            return send_from_directory(dir, filename)

        # @TODO Return 404 template if it exists
        return "Not found", 404

    def get_context_from_gdoc(self, global_values=True):
        """Wrap getting context in a simple caching mechanism."""
        try:
            start = int(time.time())
            if start > self.expires:
                self.spreadsheet_data = self._get_context_from_gdoc(global_values=global_values, **self.project.GOOGLE_DOC)
                end = int(time.time())
                ttl = (end - start) * 5
                self.expires = end + ttl
            return self.spreadsheet_data
        except AttributeError:
            return {}

    def _get_context_from_gdoc(self, key, account=None, password=None,
                              key_mode=False, global_values=True):
        """
        Turn a google doc into a Flask template context. The 'values' worksheet
        name is reserved for top-level of context namespace.
        """
        client = SpreadsheetsService()

        if account or password:
            client.email = account
            client.password = password
            client.ProgrammaticLogin()
            visibility = "private"
        else:
            visibility = "public"

        feed = client.GetWorksheetsFeed(key,
                                        visibility=visibility,
                                        projection='values')
        context = {'last_updated': feed.updated.text}
        for entry in feed.entry:
            worksheet_id = entry.id.text.rsplit('/',1)[1]

            data_feed = client.GetListFeed(key, worksheet_id,
                                           visibility=visibility,
                                           projection="values")

            if entry.title.text == 'values':
                for row in data_feed.entry:
                    text = self.parse_text_for_numbers(row.custom['value'].text)
                    worksheet_key = slughifi(row.custom['key'].text)
                    context[worksheet_key] = text
            elif len(data_feed.entry):
                headers = self._get_headers_from_worksheet(client, key,
                                                           worksheet_id,
                                                           visibility)
                worksheet_key = slughifi(entry.title.text)

                if 'key' in headers:
                    context[worksheet_key] = OrderedDict()
                    is_dict = True
                else:
                    is_dict = False
                    context[worksheet_key] = []

                for i, row in enumerate(data_feed.entry):
                    row_dict = OrderedDict()
                    for header in headers:
                        try:
                            header_key = slughifi(header)
                            value = row.custom[header_key.replace('_', '')].text
                            row_dict[header_key] = self.parse_text_for_numbers(value)
                        except KeyError:
                            pass
                    if is_dict:
                        k = slughifi(row.custom['key'].text)
                        context[worksheet_key][k] = row_dict
                    else:
                        context[worksheet_key].append(row_dict)
        return context

    def parse_text_for_numbers(self, value):
        if value is not None:
            try:
                value = int(value)
                return value
            except ValueError:
                pass

            try:
                value = float(value)
                return value
            except ValueError:
                pass

        return value

    def _get_headers_from_worksheet(self, client, key, worksheet_id,
                                    visibility):
        """Get headers in correct order."""
        headers = []
        query = CellQuery()
        query.max_row = '1'
        query.min_row = '1'
        cell_feed = client.GetCellsFeed(key, worksheet_id, query=query,
                                        visibility=visibility,
                                        projection='values')
        for cell in cell_feed.entry:
            headers.append(cell.cell.text)
        return headers
