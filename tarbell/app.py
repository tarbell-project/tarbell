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
from scrubber import Scrubber
from slughifi import slughifi


def silent_none(value):
    if value is None:
        return ''
    return value


class TarbellScrubber(Scrubber):
    disallowed_tags_save_content = set((
        'blink', 'body', 'html', 'runtime:topic'
    ))


class TarbellSite:
    def __init__(self, projects_path):
        self.app = Flask(__name__)

        self.app.jinja_env.finalize = silent_none  # Don't print "None"
        self.app.debug = True  # Always debug

        self.projects_path = projects_path
        self.projects = self.load_projects()

        self.app.add_url_rule('/<path:template>', view_func=self.preview)
        self.app.add_template_filter(self.process_text, 'process_text')
        self.app.add_template_filter(slughifi, 'slugify')

    def walk_projects(self):
        for dirpath, dirnames, filenames in os.walk(self.projects_path):
            dirnames[:] = [
                dn for dn in dirnames
                if not dn.startswith('.') and not dn.startswith('_')]
            yield dirpath, dirnames, filenames

    def load_projects(self):
        projects = {}
        prefix_loaders = []
        loaders = []

        for root, dirs, files in self.walk_projects():
            if 'config.py' in files:
                # Load configuration
                name = root.split('/')[-1]
                filename, pathname, description = imp.find_module('config', [root])
                project = imp.load_module(name, filename, pathname, description)

                # Get root path or just use pathname
                try:
                    path = project.URL_ROOT
                except AttributeError:
                    project.URL_ROOT = name
                    path = name

                try:
                    project.DONT_PUBLISH
                except AttributeError:
                    project.DONT_PUBLISH = False

                try:
                    project.CREATE_JSON
                except AttributeError:
                    project.CREATE_JSON = True

                # Register with microcopy
                projects[path] = project

                # Register as flask blueprint
                try:
                    url_prefix = None
                    if path:
                        url_prefix = '/' + path
                    self.app.register_blueprint(project.blueprint,
                                                url_prefix=url_prefix)
                except AttributeError:
                    pass

                # Get template dirs
                if path == '' and 'templates' in dirs:
                    loader = FileSystemLoader(os.path.join(root, 'templates'))
                    loaders.append(loader)
                if 'templates' in dirs:
                    loader = FileSystemLoader(os.path.join(root, 'templates'))
                    prefix_loaders.append((path, loader))

        if len(prefix_loaders):
            loaders.append(PrefixLoader(dict(prefix_loaders)))

        self.app.jinja_loader = ChoiceLoader(loaders)

        return projects

    def process_text(self, text, scrub=True):
        try:
            if scrub:
                text = TarbellScrubber().scrub(text)
            return Markup(text)
        except TypeError:
            return ""

    def preview(self, template, context=None, preview_mode=1, key_mode=False):
        """ Preview a template/path """
        path_parts = template.split('/')

        if path_parts[0] in self.projects.keys():
            project = self.projects[path_parts[0]]
            root = path_parts[0]
        else:
            project = self.projects.get('')
            root = ''

        if project:
            pagename = path_parts[-1][:-5]
            if template.endswith('/'):
                template += 'index.html'
                pagename = 'index'
            if template in self.projects.keys():
                template += '/index.html'
                pagename = 'index'

            ## Serve JSON
            if project.CREATE_JSON and len(path_parts) > 2 and path_parts[-2] == 'json' and template.endswith('.json'):
                try:
                    if not context:
                        context = self.get_context_from_gdoc(key_mode=key_mode,
                            global_values=False,**project.GOOGLE_DOC)
                    worksheet = path_parts[-1][:-5]
                    return Response(json.dumps(context[worksheet]),
                                    mimetype="application/json")
                except:
                    return 'error!', 404

            ## Serve static
            if not template.endswith('.html'):
                path = os.path.join(self.projects_path, project.__name__, 'static')
                if root != '':
                    template = '/'.join(path_parts[1:])
                return send_from_directory(path, template)

            if not key_mode:
                key_mode = request.values.has_key('keys')

            template_context = {
                "pageroot": project.URL_ROOT,
                "cache_buster": time.time(),
                "filename": template,
                "pagename": pagename,
                "project": project.__name__,
                "preview_mode": preview_mode,
                "TARBELL_PROJECTS": self.projects,
            }

            ## Get context from config
            try:
                template_context.update(project.DEFAULT_CONTEXT)
            except AttributeError:
                pass

            ## Get context from google doc
            try:
                if not context:
                    context = self.get_context_from_gdoc(key_mode=key_mode,
                                                         **project.GOOGLE_DOC)
                template_context.update(context)
            except AttributeError: 
                pass

            return render_template("%s" % template, **template_context)
        else:
            return 'error!', 404

    def get_context_from_gdoc(self, key, account=None, password=None,
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

            if global_values is True and entry.title.text == 'values':
                for row in data_feed.entry:
                    text = self.parse_text_for_numbers(row.custom['value'].text)
                    context[row.custom['key'].text] = text
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
                        k = slug_hifi(row.custom['key'].text)
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

    def render_templates(self, output_root, project_name=None):
        shutil.rmtree(output_root, ignore_errors=True)
        print "Rendering templates."
        print

        if project_name:
            projects = [self.projects[project_name]]
            if '' in self.projects.keys():
                projects.insert(0, self.projects.get(''))
        else:
            projects = self.projects.values()

        for project in projects:
            if project_name or not project.DONT_PUBLISH:
                output_dir = os.path.join(output_root, project.URL_ROOT)

                print "Generating project '%s' in %s" % (project.__name__, output_dir)
                if not self.copy_static(project, output_dir):
                    os.mkdir(output_dir)
                if project.CREATE_JSON is True:
                    self.copy_json(project, output_dir)
                self.copy_pages(project, output_dir)
                print
            else:
                print "Skipping %s" % project.__name__
                print

        return True

    def copy_static(self, project, output_dir):
        # Copy static or make directory for project
        static_dir = os.path.join(self.projects_path, project.__name__, 'static')
        if os.path.exists(static_dir):
            shutil.copytree(static_dir, output_dir)
            return True
            print '-- Static dir copied to %s.' % os.path.join(output_dir, 'static')

    def copy_pages(self, project, output_dir):
        templates_dir = os.path.join(self.projects_path, project.__name__, 'templates')
        try:
            context = self.get_context_from_gdoc(**project.GOOGLE_DOC)
        except AttributeError:
            context = {}
        for path, dirnames, filenames in os.walk(templates_dir):
            for fn in filenames:
                if fn[0] != '_' and fn[0] != '.':
                    tpath = "%s/%s" % (project.URL_ROOT, fn)
                    with self.app.test_request_context('%s' % tpath):
                        try:
                            content = self.preview(tpath, context,
                                                   preview_mode=0)
                            codecs.open(os.path.join(output_dir, fn), "w",
                                        encoding='utf-8').write(content)
                            print "-- Created page %s" % os.path.join(output_dir, fn)
                        except Exception, e:
                            print "Exception (%s) for %s" % (e, tpath)

    def copy_json(self, project, output_dir):
        ## Get context from google doc
        try:
            context = self.get_context_from_gdoc(global_values=False,
                                                 **project.GOOGLE_DOC)
            os.makedirs(os.path.join(output_dir, 'json'))
            for k, v in context.items():
                codecs.open(os.path.join(output_dir, "json/%s.json" % k),
                            "w", encoding='utf-8').write(json.dumps(v))
                print "-- Created JSON %s" % os.path.join(output_dir, "json/%s.json" % k)
        except AttributeError:
            print "-- No Google doc configured for %s." % project.__name__
