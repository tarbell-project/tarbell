from flask import Flask, render_template, send_from_directory, Response
import time
import os
from jinja2 import FileSystemLoader, ChoiceLoader
from ordereddict import OrderedDict
from .oauth import get_drive_api
import json
import imp
from slughifi import slughifi
import mimetypes
import xlrd
from string import uppercase
from werkzeug.wsgi import FileWrapper
TTL_MULTIPLIER = 5


def silent_none(value):
    if value is None:
        return ''
    return value


class TarbellSite:
    def __init__(self, path):
        self.app = Flask(__name__)

        self.app.jinja_env.finalize = silent_none  # Don't print "None"
        self.app.debug = True  # Always debug

        self.path = path
        self.projects = self.load_projects()
        self.project = self.projects[0][1]

        self.client = get_drive_api(self.path)
        self.data = {}
        self.expires = 0

        self.app.add_url_rule('/', view_func=self.preview)
        self.app.add_url_rule('/<path:path>', view_func=self.preview)
        self.app.add_template_filter(slughifi, 'slugify')

    def filter_files(self, path):
        for dirpath, dirnames, filenames in os.walk(path):
            dirnames[:] = [
                dn for dn in dirnames
                if not dn.startswith('.') and not dn.startswith('_')
                ]
            filenames[:] = [
                fn for fn in filenames
                if not fn.startswith('.') and not fn.startswith('_')
                ]
            yield dirpath, dirnames, filenames

    def sort_modules(self, x, y):
        if x[0] == "base":
            return 1
        return -1

    def load_projects(self):
        projects = []
        for root, dirs, files in self.filter_files(self.path):
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
        if self.project.CREATE_JSON and path == 'data.json':
            context = self.get_context_from_gdoc()
            return Response(json.dumps(context), mimetype="application/json")

        ## Detect files
        filepath = None
        for name, project, root in self.projects:
            fullpath = os.path.join(root, path)
            try:
                with open(fullpath):
                    mimetype, encoding = mimetypes.guess_type(fullpath)
                    filepath = fullpath
            except IOError:
                pass

        if filepath and mimetype and mimetype.startswith("text/"):
            context = self.project.DEFAULT_CONTEXT
            context.update(self.get_context_from_gdoc())
            rendered = render_template(path, **context)
            return Response(rendered, mimetype=mimetype)
        elif filepath:
            dir, filename = os.path.split(filepath)
            return send_from_directory(dir, filename)

        # @TODO Return 404 template if it exists, use Response object
        return "Not found", 404

    def get_context_from_gdoc(self):
        """Wrap getting context in a simple caching mechanism."""
        try:
            start = int(time.time())
            if start > self.expires:
                self.data = self._get_context_from_gdoc(
                    **self.project.GOOGLE_DOC)
                end = int(time.time())
                ttl = (end - start) * TTL_MULTIPLIER
                self.expires = end + ttl
            return self.data
        except AttributeError:
            return {}

    def _get_context_from_gdoc(self, key, **kwargs):
        data = {}

        # Download xlsx version of spreadsheet
        spreadsheet_file = self.client.files().get(fileId=key).execute()
        links = spreadsheet_file.get('exportLinks')
        downloadurl = links.get('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp, content = self.client._http.request(downloadurl)

        # Open xlsx contents
        workbook = xlrd.open_workbook(file_contents=content)
        worksheets = workbook.sheet_names()
        for worksheet_name in worksheets:
            worksheet = workbook.sheet_by_name(worksheet_name)
            worksheet.name = slughifi(worksheet.name)
            headers = self.make_headers(worksheet)
            worksheet_data = self.make_worksheet_data(headers, worksheet)
            data[worksheet.name] = worksheet_data

        # Copy values into global namespace
        if 'values' in worksheets:
            for k, v in data['values'].items():
                if not data.get(k):
                    data[k] = v
                else:
                    self.app.logger.warning("There is both a worksheet and a "
                            "value named '{0}'. The worksheet data will be "
                            "preserved."
                           .format(k))
        return data

    def make_headers(self, worksheet):
        # Make headers
        headers = {}
        cell_idx = 0
        while cell_idx < worksheet.ncols:
            cell_type = worksheet.cell_type(0, cell_idx)
            if cell_type == 1:
                header = slughifi(worksheet.cell_value(0, cell_idx))
                if not header.startswith("_"):
                    headers[cell_idx] = header
            cell_idx += 1
        return headers

    def make_worksheet_data(self, headers, worksheet):
        # Make data
        data = []
        row_idx = 1
        while row_idx < worksheet.nrows:
            cell_idx = 0
            row_dict = OrderedDict()
            while cell_idx < worksheet.ncols:
                cell_type = worksheet.cell_type(row_idx, cell_idx)
                if cell_type > 0 and cell_type < 5:
                    cell_value = worksheet.cell_value(row_idx, cell_idx)
                    try:
                        row_dict[headers[cell_idx]] = cell_value
                    except KeyError:
                        try:
                            column = uppercase[cell_idx]
                        except IndexError:
                            column = cell_idx
                        self.app.logger.warning("There is no header for cell with "
                               "value '{0}' in column '{1}' of '{2}'" .format(
                                   cell_value, column, worksheet.name))
                cell_idx += 1
            data.append(row_dict)
            row_idx += 1

        # Magic key handling
        if 'key' in headers.values():
            keyed_data = OrderedDict()
            for row in data:
                key = slughifi(row['key'])
                if keyed_data.get(key):
                    self.app.logger.warning("There is already a key named '{0}' with value "
                           "'{1}' in '{2}'. It is being overwritten with "
                           "value '{3}'.".format(key,
                                   keyed_data.get(key),
                                   worksheet.name,
                                   row))

                # Magic values worksheet
                if worksheet.name == "values":
                    keyed_data[key] = row['value']
                else:
                    keyed_data[key] = row
            data = keyed_data

        return data

    def generate_static_site(self, output_root):
        for name, project, project_path in self.projects:
            for root, dirs, files in self.filter_files(project_path):
                files[:] = [
                    filename for filename in files
                    if not filename.endswith('.py') and not filename.endswith('.pyc')
                    ]
                for filename in files:
                    # Strip out full filesystem paths
                    dirname = root.replace(project_path, "")
                    path = "{0}/{1}".format(dirname, filename)
                    if path.startswith("/"):
                        path = path[1:]
                    output_path = os.path.join(output_root, path)
                    output_dir = os.path.dirname(output_path)

                    # @TODO account for overwriting
                    self.app.logger.info("Writing {0}".format(output_path))
                    with self.app.test_request_context():
                        preview = self.preview(path)
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        with open(output_path, "wb") as f:
                            if isinstance(preview.response, FileWrapper):
                                f.write(preview.response.file.read())
                            else:
                                f.write(preview.data)
