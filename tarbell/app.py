# -*- coding: utf-8 -*-
import codecs
import csv
import datetime
import dateutil
import fnmatch
import imp
import markdown as md
import mimetypes
import os
import re
import requests
import sys
import time
import traceback
import xlrd

from httplib import BadStatusLine
from flask import Flask, Blueprint, render_template, send_from_directory, Response, g, jsonify
from flask_frozen import Freezer, walk_directory
from jinja2 import contextfunction, Markup
from jinja2.loaders import BaseLoader
from jinja2.utils import open_if_exists
from jinja2.exceptions import TemplateNotFound
from jinja2._compat import string_types
from pprint import pformat
from slughifi import slughifi
from string import uppercase
from werkzeug.wsgi import FileWrapper
from clint.textui import puts

from .errors import MergedCellError
from .oauth import get_drive_api
from .hooks import hooks

# in seconds
SPREADSHEET_CACHE_TTL = 4

# all spreadsheet values except empty string
VALID_CELL_TYPES = range(1, 5)

# pass template variables to files with these mimetypes
TEMPLATE_TYPES = (
    "text/html",
)

EXCLUDES = ['.git/*', '.git', '.gitignore', '.*', '*.pyc', '*.py', '_*']


def split_template_path(template):
    """
    Split a path into segments and perform a sanity check.  If it detects
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
    """
    Custom loader for Tarbell templates; searches Tarbell's template directories (first _blueprint,
    then the project itself) for matching templates.
    """

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


def silent_none(value):
    """
    Return `None` values as empty strings
    """
    if value is None:
        return ''
    return value


def pprint_lines(value):
    """
    Pretty print lines
    """
    pformatted = pformat(value, width=1, indent=4)
    formatted = "{0}\n {1}\n{2}".format(
        pformatted[0],
        pformatted[1:-1],
        pformatted[-1]
    )
    return Markup(formatted)


def process_xlsx(content):
    """
    Turn Excel file contents into Tarbell worksheet data
    """
    data = {}
    workbook = xlrd.open_workbook(file_contents=content)
    worksheets = [w for w in workbook.sheet_names() if not w.startswith('_')]
    for worksheet_name in worksheets:
        if worksheet_name.startswith('_'):
            continue

        worksheet = workbook.sheet_by_name(worksheet_name)

        merged_cells = worksheet.merged_cells
        if len(merged_cells):
            raise MergedCellError(worksheet.name, merged_cells)

        worksheet.name = slughifi(worksheet.name)
        headers = make_headers(worksheet)
        worksheet_data = make_worksheet_data(headers, worksheet)
        data[worksheet.name] = worksheet_data
    return data


def copy_global_values(data):
    """
    Copy values worksheet into global namespace.
    """
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
    """
    Make headers from worksheet
    """
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
    """
    Make data from worksheet
    """
    data = []
    row_idx = 1
    while row_idx < worksheet.nrows:
        cell_idx = 0
        row_dict = {}
        while cell_idx < worksheet.ncols:
            cell_type = worksheet.cell_type(row_idx, cell_idx)
            if cell_type in VALID_CELL_TYPES:
                cell_value = worksheet.cell_value(row_idx, cell_idx)
                try:
                    if cell_type == 2 and cell_value.is_integer():
                        cell_value = int(cell_value)
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
                    if value not in ("", None):
                        keyed_data[key] = value
                else:
                    keyed_data[key] = row

        data = keyed_data

    return data


def markdown(value):
    """
    Run text through markdown process
    """
    return Markup(md.markdown(value))


def process_text(text):
    """
    Return markup or empty string
    """
    try:
        return Markup(text)
    except TypeError:
        return u''


def format_date(value, format='%b. %d, %Y', convert_tz=None):
    """
    Format an Excel date.
    """
    if isinstance(value, float) or isinstance(value, int):
        seconds = (value - 25569) * 86400.0
        parsed = datetime.datetime.utcfromtimestamp(seconds)
    else:
        parsed = dateutil.parser.parse(value)
    if convert_tz:
        local_zone = dateutil.tz.gettz(convert_tz)
        parsed = parsed.astimezone(tz=local_zone)

    if format:
        return parsed.strftime(format)
    else:
        return parsed

class TarbellSite:
    def __init__(self, path, client_secrets_path=None, quiet=False):
        self.app = Flask(__name__)

        self.quiet = quiet

        self.app.jinja_env.finalize = silent_none  # Don't print "None"
        self.app.debug = True  # Always debug

        self.path = path
        self.project, self.base = self.load_project(path)

        self.data = {}
        self.hooks = self.process_hooks(hooks)
        self.expires = 0

        # add routes
        self.app.add_url_rule('/', view_func=self.preview)
        self.app.add_url_rule('/<path:path>', view_func=self.preview)
        self.app.add_url_rule('/data.json', view_func=self.data_json)

        self.app.add_template_filter(format_date, 'format_date')
        self.app.add_template_filter(markdown, 'markdown')
        self.app.add_template_filter(slughifi, 'slugify')
        self.app.add_template_filter(pprint_lines, 'pprint_lines')
        self.app.add_template_filter(process_text, 'process_text')
        self.app.add_template_filter(process_text, 'markup')
        self.app.jinja_env.globals.update(render_file=self.render_file)
        self.app.jinja_env.globals.update(read_file=self.read_file)

        self.app.before_request(self.add_site_to_context)
        self.app.after_request(self.never_cache_preview)

        # centralized freezer setup
        self.app.config.setdefault('FREEZER_RELATIVE_URLS', True)
        self.app.config.setdefault('FREEZER_REMOVE_EXTRA_FILES', False)
        self.app.config.setdefault('FREEZER_DESTINATION', 
            os.path.join(os.path.realpath(self.path), '_site'))

        self.freezer = Freezer(self.app) 
        self.freezer.register_generator(self.find_files)

    def add_site_to_context(self):
        """
        Add current Tarbell object to Flask's `g`
        """
        g.current_site = self

    def never_cache_preview(self, response):
        """
        Ensure preview is never cached
        """
        response.cache_control.max_age = 0
        response.cache_control.no_cache = True
        response.cache_control.must_revalidate = True
        response.cache_control.no_store = True
        return response

    def read_file(self, path, absolute=False, encoding='utf-8'):
        """
        Read the file at `path`. If `absolute` is True, use absolute path,
        otherwise path is assumed to be relative to Tarbell template root dir.
        """
        if not absolute:
            path = os.path.join(self.path, path)

        try:
            return codecs.open(path, 'r', encoding).read()
        except IOError:
            return None

    @contextfunction
    def render_file(self, context, path, absolute=False):
        """
        Render a file with the current context
        """
        return render_template(path, **context)

    def process_hooks(self, hooks):
        """
        Process all project hooks
        """
        try:
            enabled_hooks = self.project.HOOKS
        except AttributeError:
            return hooks

    def call_hook(self, hook, *args, **kwargs):
        """
        Calls each registered hook
        """
        for function in self.hooks[hook]:
            function.__call__(*args, **kwargs)

    def _get_base(self, path):
        """
        Get project blueprint
        """
        base = None

        # Slightly ugly DRY violation for backwards compatibility with old
        # "_base" convention
        if os.path.isdir(os.path.join(path, "_blueprint")):
            base_dir = os.path.join(path, "_blueprint/")
            # Get the blueprint template and register it as a blueprint
            if os.path.exists(os.path.join(base_dir, "blueprint.py")):
                filename, pathname, description = imp.find_module('blueprint', [base_dir])
                base = imp.load_module('blueprint', filename, pathname, description)
                self.blueprint_name = "_blueprint"
            else:
                puts("No _blueprint/blueprint.py file found")
        elif os.path.isdir(os.path.join(path, "_base")):
            puts("Using old '_base' convention")
            base_dir = os.path.join(path, "_base/")
            if os.path.exists(os.path.join(base_dir, "base.py")):
                filename, pathname, description = imp.find_module('base', [base_dir])
                base = imp.load_module('base', filename, pathname, description)
                self.blueprint_name = "_base"
            else:
                puts("No _base/base.py file found")

        if base:
            base.base_dir = base_dir
            self.app.register_blueprint(base.blueprint)

        return base

    def load_project(self, path):
        """
        Load a Tarbell project
        """
        base = self._get_base(path)

        filename, pathname, description = imp.find_module('tarbell_config', [path])
        project = imp.load_module('project', filename, pathname, description)

        try:
            self.key = project.SPREADSHEET_KEY
            self.client = get_drive_api()
        except AttributeError:
            self.key = None
            self.client = None

        try:
            project.CREATE_JSON
        except AttributeError:
            project.CREATE_JSON = False

        try:
            project.S3_BUCKETS
        except AttributeError:
            project.S3_BUCKETS = {}

        try:
            project.EXCLUDES
        except AttributeError:
            project.EXCLUDES = []

        if base:
            try:
                base.EXCLUDES
            except AttributeError:
                base.EXCLUDES = []

            # Merge excludes
            project.EXCLUDES = EXCLUDES + base.EXCLUDES + list(set(project.EXCLUDES) - set(base.EXCLUDES))

        # merge project template types with defaults
        project.TEMPLATE_TYPES = set(getattr(project, 'TEMPLATE_TYPES', [])) | set(TEMPLATE_TYPES)

        try:
            project.DEFAULT_CONTEXT
        except AttributeError:
            project.DEFAULT_CONTEXT = {}

        project.DEFAULT_CONTEXT.update({
            "PROJECT_PATH": self.path,
            "ROOT_URL": "127.0.0.1:5000",
            "SPREADSHEET_KEY": self.key,
            "BUCKETS": project.S3_BUCKETS,
            "SITE": self,
        })

        # Set up template loaders
        template_dirs = [path]
        if base:
            template_dirs.append(base.base_dir)
        error_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'error_templates')
        template_dirs.append(error_path)

        self.app.jinja_loader = TarbellFileSystemLoader(template_dirs)

        # load the project blueprint, if it exists
        if hasattr(project, 'blueprint') and isinstance(project.blueprint, Blueprint):
            self.app.register_blueprint(project.blueprint)

        return project, base

    def _resolve_path(self, path):
        """
        Resolve static file paths
        """
        filepath = None
        mimetype = None

        for root, dirs, files in self.filter_files(self.path):
            # Does it exist in error path?
            error_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'error_templates', path)
            try:
                with open(error_path):
                    mimetype, encoding = mimetypes.guess_type(error_path)
                    filepath = error_path
            except IOError:
                pass

            # Does it exist in Tarbell blueprint?
            if self.base:
                basepath = os.path.join(root, self.blueprint_name, path)
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

        return filepath, mimetype

    def data_json(self, extra_context=None, publish=False):
        """
        Serve site context as JSON. Useful for debugging.
        """
        if not self.project.CREATE_JSON:
            # nothing to see here, but the right mimetype
            return jsonify()

        if not self.data:
            # this sets site.data by spreadsheet or gdoc
            self.get_context(publish)

        return jsonify(self.data)

    def preview(self, path=None, extra_context=None, publish=False):
        """
        Serve up a project path
        """
        try:
            self.call_hook("preview", self)

            if path is None:
                path = 'index.html'

            # Detect files
            filepath, mimetype = self._resolve_path(path)

            # Serve dynamic
            if filepath and mimetype and mimetype in self.project.TEMPLATE_TYPES:
                context = self.get_context(publish)
                context.update({
                    "PATH": path,
                    "PREVIEW_SERVER": not publish,
                    "TIMESTAMP": int(time.time()),
                })
                if extra_context:
                    context.update(extra_context)

                rendered = render_template(path, **context)
                return Response(rendered, mimetype=mimetype)

            # Serve static
            if filepath:
                dir, filename = os.path.split(filepath)
                return send_from_directory(dir, filename)

        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            try:
                # Find template with name of error
                cls = e.__class__
                ex_type, ex, tb = sys.exc_info()

                context = self.project.DEFAULT_CONTEXT
                context.update({
                    'PATH': path,
                    'traceback': traceback.format_exception(ex_type, ex, tb),
                    'e': e,
                })
                if extra_context:
                    context.update(extra_context)

                try:
                    error_path = '_{0}.{1}.html'.format(cls.__module__, cls.__name__)
                    rendered = render_template(error_path, **context)
                except TemplateNotFound:
                    # Find template without underscore prefix, @TODO remove in v1.1
                    error_path = '{0}.{1}.html'.format(cls.__module__, cls.__name__)
                    rendered = render_template(error_path, **context)

                return Response(rendered, mimetype="text/html")
            except TemplateNotFound:
                # Otherwise raise old error
                raise ex_type, ex, tb

        # Last ditch effort -- see if path has "index.html" underneath it
        if not path.endswith("index.html"):
            if not path.endswith("/"):
                path = "{0}/".format(path)
            path = "{0}{1}".format(path, "index.html")
            return self.preview(path)

        # It's a 404
        if path.endswith('/index.html'):
            path = path[:-11]
        rendered = render_template("404.html", PATH=path)
        return Response(rendered, status=404)

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
                context.update(self.get_context_from_xlsx())
        except AttributeError:
            context.update(self.get_context_from_gdoc())

        return context

    def get_context_from_xlsx(self):
        """
        Get context from an Excel file
        """
        if re.search('^(http|https)://', self.project.CONTEXT_SOURCE_FILE):
            resp = requests.get(self.project.CONTEXT_SOURCE_FILE)
            content = resp.content
        else:
            try:
                with open(self.project.CONTEXT_SOURCE_FILE) as xlsxfile:
                    content = xlsxfile.read()
            except IOError:
                filepath = "%s/%s" % (
                    os.path.abspath(self.path),
                    self.project.CONTEXT_SOURCE_FILE)
                with open(filepath) as xlsxfile:
                    content = xlsxfile.read()

        data = process_xlsx(content)
        if 'values' in data:
            data = copy_global_values(data)

        return data

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
        """
        Wrap getting context from Google sheets in a simple caching mechanism.
        """
        try:
            start = int(time.time())
            if not self.data or start > self.expires:
                self.data = self._get_context_from_gdoc(self.project.SPREADSHEET_KEY)
                end = int(time.time())
                ttl = getattr(self.project, 'SPREADSHEET_CACHE_TTL',
                              SPREADSHEET_CACHE_TTL)
                self.expires = end + ttl
            return self.data
        except AttributeError:
            return {}

    def _get_context_from_gdoc(self, key):
        """
        Create a Jinja2 context from a Google spreadsheet.
        """
        try:
            content = self.export_xlsx(key)
            data = process_xlsx(content)
            if 'values' in data:
                data = copy_global_values(data)
            return data
        except BadStatusLine:
            # Stale connection, reset API and data
            puts("Connection reset, reloading drive API")
            self.client = get_drive_api()
            return self._get_context_from_gdoc(key)

    def export_xlsx(self, key):
        """
        Download xlsx version of spreadsheet.
        """
        spreadsheet_file = self.client.files().get(fileId=key).execute()
        links = spreadsheet_file.get('exportLinks')
        downloadurl = links.get('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp, content = self.client._http.request(downloadurl)
        return content

    def generate_static_site(self, output_root=None, extra_context=None):
        """
        Bake out static site
        """
        self.app.config['BUILD_PATH'] = output_root

        # use this hook for registering URLs to freeze
        self.call_hook("generate", self, output_root, extra_context)

        if output_root is not None:
            # realpath or this gets generated relative to the tarbell package
            self.app.config['FREEZER_DESTINATION'] = os.path.realpath(output_root)

        self.freezer.freeze()

    def filter_files(self, path):
        """
        Exclude files based on blueprint and project configuration as well as hidden files.
        """
        excludes = r'|'.join([fnmatch.translate(x) for x in self.project.EXCLUDES]) or r'$.'
        for root, dirs, files in os.walk(path, topdown=True):
            dirs[:] = [d for d in dirs if not re.match(excludes, d)]
            dirs[:] = [os.path.join(root, d) for d in dirs]
            rel_path = os.path.relpath(root, path)

            paths = []
            for f in files:
                if rel_path == '.':
                    file_path = f
                else:
                    file_path = os.path.join(rel_path, f)
                if not re.match(excludes, file_path):
                    paths.append(f)

            files[:] = paths
            yield root, dirs, files

    def find_files(self):
        """
        Find all file paths for publishing, yield (urlname, kwargs)
        """
        # yield blueprint paths first
        if getattr(self, 'blueprint_name', None):
            for path in walk_directory(os.path.join(self.path, self.blueprint_name), ignore=self.project.EXCLUDES):
                yield 'preview', {'path': path}

        # then yield project paths
        for path in walk_directory(self.path, ignore=self.project.EXCLUDES):
            yield 'preview', {'path': path}
