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
import mimetypes

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

        self.app.add_url_rule('/', view_func=self.preview)
        self.app.add_url_rule('/<path:path>', view_func=self.preview)
        self.app.add_template_filter(self.process_text, 'process_text')
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

            #try:
                #project.CREATE_JSON
            #except AttributeError:
                #project.CREATE_JSON = True

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

    def process_text(self, text, scrub=True):
        try:
            if scrub:
                text = TarbellScrubber().scrub(text)
            return Markup(text)
        except TypeError:
            return ""

    def preview(self, path=None, context=None, preview_mode=1, key_mode=False):
        """ Preview a template/path """
        if path is None:
            path = 'index.html'
        if path.endswith('/'):
            path += 'index.html'

        ## Serve JSON
        #if self.project.CREATE_JSON and len(path_parts) > 2 and path_parts[-2] == 'json' and template.endswith('.json'):
            #try:
                #if not context:
                    #context = self.get_context_from_gdoc(key_mode=key_mode,
                        #global_values=False,**project.GOOGLE_DOC)
                #worksheet = path_parts[-1][:-5]
                #return Response(json.dumps(context[worksheet]),
                                #mimetype="application/json")
            #except:
                #return 'error!', 404

        ## Serve static
        file = False
        filepath = None
        #print self.projects
        for name, project, root in self.projects:
            fullpath = os.path.join(root, path)
            try:
                with open(fullpath) as file:
                    mimetype, encoding = mimetypes.guess_type(fullpath)
                    filepath = fullpath
            except IOError: pass

        if filepath:
            if mimetype.startswith("text/"):
                template_context = {}
                ## Get context from project config
                try:
                    template_context.update(self.projects[0][1].DEFAULT_CONTEXT)
                    print "worked"
                except AttributeError:
                    print "didn't"
                    pass

                ### Get context from google doc
                try:
                    if not context:
                        context = self.get_context_from_gdoc(key_mode=key_mode,
                                                             **self.project.GOOGLE_DOC)
                    template_context.update(context)
                except AttributeError:
                    pass

                rendered = render_template(path, **template_context)
                return Response(rendered, mimetype=mimetype)
            else:
                dir, filename = os.path.split(filepath)
                return send_from_directory(dir, filename)

        return "error", 404

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
