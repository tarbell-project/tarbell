import os
import json
import imp
import mimetypes
import xlrd
import csv
import re
import requests
import time

from httplib import BadStatusLine
from flask import Flask, render_template, send_from_directory, Response
from jinja2 import Markup, TemplateSyntaxError
from jinja2.loaders import BaseLoader
from jinja2.utils import open_if_exists
from jinja2.exceptions import TemplateNotFound
from jinja2._compat import string_types
from pprint import pformat
from slughifi import slughifi
from string import uppercase
from werkzeug.wsgi import FileWrapper
from utils import filter_files
from clint.textui import puts, colored

from .oauth import get_drive_api

# in seconds
SPREADSHEET_CACHE_TTL = 4 

# pass template variables to files with these mimetypes
TEMPLATE_TYPES = [
    "text/html",
    "text/css",
    "application/javascript",
]

def split_template_path(template):
    """Split a path into segments and perform a sanity check.  If it detects
    '..' in the path it will raise a `TemplateNotFound` error.
    """
    pieces = []
    for piece in template.split('/'):
        if os.path.sep in piece \
           or (os.path.altsep and os.path.altsep in piece) or \
           piece == os.path.pardir:
            raise TemplateNotFound(template)
        elif piece and piece != '.':
            pieces.append(piece)
    return pieces

class TarbellFileSystemLoader(BaseLoader):
    def __init__(self, searchpath, encoding='utf-8'):
        if isinstance(searchpath, string_types):
            searchpath = [searchpath]
        self.searchpath = list(searchpath)
        self.encoding = encoding

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        for searchpath in self.searchpath:
            filename = os.path.join(searchpath, *pieces)
            f = open_if_exists(filename)
            if f is None:
                continue
            try:
                contents = f.read().decode(self.encoding)
            finally:
                f.close()

            mtime = os.path.getmtime(filename)

            def uptodate():
                try:
                    return os.path.getmtime(filename) == mtime
                except OSError:
                    return False
            return contents, filename, uptodate
        raise TemplateNotFound(template)

    def list_templates(self):
        found = set()
        for searchpath in self.searchpath:
            for dirpath, dirnames, filenames in filter_files(searchpath):
                for filename in filenames:
                    template = os.path.join(dirpath, filename) \
                        [len(searchpath):].strip(os.path.sep) \
                                          .replace(os.path.sep, '/')
                    if template[:2] == './':
                        template = template[2:]
                    if template not in found:
                        found.add(template)
        return sorted(found)


def silent_none(value):
    if value is None:
        return ''
    return value


def pprint_lines(value):
    pformatted = pformat(value, width=1, indent=4)
    formatted = "{0}\n {1}\n{2}".format(
        pformatted[0],
        pformatted[1:-1],
        pformatted[-1]
    )
    return Markup(formatted)


def process_xlsx(content):
    """Turn Excel file contents into Tarbell worksheet data"""
    data = {}
    workbook = xlrd.open_workbook(file_contents=content)
    worksheets = workbook.sheet_names()
    for worksheet_name in worksheets:
        worksheet = workbook.sheet_by_name(worksheet_name)
        worksheet.name = slughifi(worksheet.name)
        headers = make_headers(worksheet)
        worksheet_data = make_worksheet_data(headers, worksheet)
        data[worksheet.name] = worksheet_data
    return data


def copy_global_values(data):
    """Copy values worksheet into global namespace."""
    for k, v in data['values'].items():
        if not data.get(k):
            data[k] = v
        else:
            puts("There is both a worksheet and a "
                 "value named '{0}'. The worksheet data "
                 "will be preserved.".format(k))
    data.pop("values", None)
    return data


def make_headers(worksheet):
    """Make headers"""
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


def make_worksheet_data(headers, worksheet):
    # Make data
    data = []
    row_idx = 1
    while row_idx < worksheet.nrows:
        cell_idx = 0
        row_dict = {}
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
                        puts("There is no header for cell with value '{0}' in column '{1}' of '{2}'" .format(
                            cell_value, column, worksheet.name
                        ))
            cell_idx += 1
        data.append(row_dict)
        row_idx += 1

    # Magic key handling
    if 'key' in headers.values():
        keyed_data = {}
        for row in data:
            if 'key' in row.keys():
                key = slughifi(row['key'])
                if keyed_data.get(key):
                    puts("There is already a key named '{0}' with value "
                           "'{1}' in '{2}'. It is being overwritten with "
                           "value '{3}'.".format(key,
                                   keyed_data.get(key),
                                   worksheet.name,
                                   row))

                # Magic values worksheet
                if worksheet.name == "values":
                    value = row.get('value')
                    if value:
                        keyed_data[key] = value
                else:
                    keyed_data[key] = row

        data = keyed_data

    return data


class TarbellSite:
    def __init__(self, path, client_secrets_path=None, quiet=False):
        self.app = Flask(__name__)

        self.quiet = quiet

        self.app.jinja_env.finalize = silent_none  # Don't print "None"
        self.app.debug = True  # Always debug

        self.path = path
        self.project, self.base = self.load_project(path)

        self.data = {}
        self.expires = 0

        self.app.add_url_rule('/', view_func=self.preview)
        self.app.add_url_rule('/<path:path>', view_func=self.preview)
        self.app.add_template_filter(slughifi, 'slugify')
        self.app.add_template_filter(pprint_lines, 'pprint_lines')

    def load_project(self, path):
        base = None
        base_dir = os.path.join(path, "_base/")

        # Get the base as register it as a blueprint
        if os.path.exists(os.path.join(base_dir, "base.py")):
            filename, pathname, description = imp.find_module('base', [base_dir])
            base = imp.load_module('base', filename, pathname, description)
            self.app.register_blueprint(base.blueprint)
        else:
            puts("No _base/base.py file found")

        filename, pathname, description = imp.find_module('tarbell_config', [path])
        project = imp.load_module('project', filename, pathname, description)

        try:
            self.key = project.SPREADSHEET_KEY
            self.client = get_drive_api(self.path)
        except AttributeError:
            self.key = None
            self.client = None

        try:
            project.CREATE_JSON
        except AttributeError:
            project.CREATE_JSON = True

        try:
            project.DEFAULT_CONTEXT
        except AttributeError:
            project.DEFAULT_CONTEXT = {}

        try:
            self.app.register_blueprint(project.blueprint)
        except AttributeError:
            pass

        # Set up template loaders
        template_dirs = [path]
        if os.path.isdir(base_dir):
            template_dirs.append(base_dir)

        self.app.jinja_loader = TarbellFileSystemLoader(template_dirs)

        return project, base

    def preview(self, path=None, extra_context=None, publish=False):
        """ Preview a project path """
        if path is None:
            path = 'index.html'

        ## Serve JSON
        if self.project.CREATE_JSON and path == 'data.json':
            context = self.get_context(publish)
            return Response(json.dumps(context), mimetype="application/json")

        ## Detect files
        filepath = None
        for root, dirs, files in filter_files(self.path):
            # Does it exist under _base?
            basepath = os.path.join(root, "_base", path)
            try:
                with open(basepath):
                    mimetype, encoding = mimetypes.guess_type(basepath)
                    filepath = basepath
            except IOError:
                pass

            # Does it exist under regular path?
            fullpath = os.path.join(root, path)
            try:
                with open(fullpath):
                    mimetype, encoding = mimetypes.guess_type(fullpath)
                    filepath = fullpath
            except IOError:
                pass

        if filepath and mimetype and mimetype in TEMPLATE_TYPES:
            context = self.get_context(publish)
            # Mix in defaults
            context.update({
                "PROJECT_PATH": self.path,
                "PREVIEW_SERVER": not publish,
                "ROOT_URL": "127.0.0.1:5000",
                "PATH": path,
                "SPREADSHEET_KEY": self.key,
            })
            if extra_context:
                context.update(extra_context)
            try:
                rendered = render_template(path, **context)
                return Response(rendered, mimetype=mimetype)
            except TemplateSyntaxError:
                puts("{0} can't be parsed by Jinja, serving static".format(colored.yellow(filepath)))

        if filepath:
            dir, filename = os.path.split(filepath)
            return send_from_directory(dir, filename)

        return Response(status=404)

    def get_context(self, publish=False):
        """
        Use optional CONTEXT_SOURCE_FILE setting to determine data source.
        Return the parsed data.

        Can be an http|https url or local file. Supports csv and excel files.
        """
        context = self.project.DEFAULT_CONTEXT
        try:
            file = self.project.CONTEXT_SOURCE_FILE
            # CSV
            if re.search(r'(csv|CSV)$', file):
                context.update(self.get_context_from_csv())
            # Excel
            if re.search(r'(xlsx|XLSX|xls|XLS)$', file):
                pass
        except AttributeError:
            context.update(self.get_context_from_gdoc())

        return context

    def get_context_from_csv(self):
        """
        Open CONTEXT_SOURCE_FILE, parse and return a context
        """
        if re.search('^(http|https)://', self.project.CONTEXT_SOURCE_FILE):
            data = requests.get(self.project.CONTEXT_SOURCE_FILE)
            reader = csv.reader(
                data.iter_lines(), delimiter=',', quotechar='"')
            ret = {rows[0]: rows[1] for rows in reader}
        else:
            try:
                with open(self.project.CONTEXT_SOURCE_FILE) as csvfile:
                    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                    ret = {rows[0]: rows[1] for rows in reader}
            except IOError:
                file = "%s/%s" % (
                    os.path.abspath(self.path),
                    self.project.CONTEXT_SOURCE_FILE)
                with open(file) as csvfile:
                    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                    ret = {rows[0]: rows[1] for rows in reader}
        ret.update({
            "CONTEXT_SOURCE_FILE": self.project.CONTEXT_SOURCE_FILE,
        })
        return ret

    def get_context_from_gdoc(self):
        """Wrap getting context in a simple caching mechanism."""
        try:
            start = int(time.time())
            if not self.data or start > self.expires:
                self.data = self._get_context_from_gdoc(self.project.SPREADSHEET_KEY)
                end = int(time.time())
                self.expires = end + SPREADSHEET_CACHE_TTL
            return self.data
        except AttributeError:
            return {}

    def _get_context_from_gdoc(self, key):
        """Create a Jinja2 context from a Google spreadsheet."""
        try:
            content = self.export_xlsx(key)
            data = process_xlsx(content)
            if 'values' in data:
                data = copy_global_values(data)
            return data
        except BadStatusLine:
            # Stale connection, reset API and data
            puts("Connection reset, reloading drive API")
            self.client = get_drive_api(self.path)
            self.data = {}
            return self._get_context_from_gdoc(key)

    def export_xlsx(self, key):
        """Download xlsx version of spreadsheet"""
        spreadsheet_file = self.client.files().get(fileId=key).execute()
        links = spreadsheet_file.get('exportLinks')
        downloadurl = links.get('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp, content = self.client._http.request(downloadurl)
        return content

    def generate_static_site(self, output_root, extra_context):
        base_dir = os.path.join(self.path, "_base/")

        for root, dirs, files in filter_files(base_dir):
            for filename in files:
                self._copy_file(root.replace("_base/", ""), filename, output_root, extra_context)

        for root, dirs, files in filter_files(self.path):
            for filename in files:
                self._copy_file(root, filename, output_root, extra_context)

    def _copy_file(self, root, filename, output_root, extra_context=None):
        # Strip out full filesystem paths
        rel_path = os.path.join(root.replace(self.path, ""), filename)
        if rel_path.startswith("/"):
            rel_path = rel_path[1:]
        output_path = os.path.join(output_root, rel_path)
        output_dir = os.path.dirname(output_path)

        if not self.quiet:
            puts("Writing {0}".format(output_path))
        with self.app.test_request_context():
            preview = self.preview(rel_path, extra_context=extra_context, publish=True)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(output_path, "wb") as f:
                if isinstance(preview.response, FileWrapper):
                    f.write(preview.response.file.read())
                else:
                    f.write(preview.data)
