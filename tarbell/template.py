# -*- coding: utf-8 -*-
"""
All template code lives here, including Jinja filters and loaders.

Filters are added to a blueprint, which can be registered on the Tarbell app.
"""
import codecs
import datetime
import dateutil
import os
from pprint import pformat
from flask import Blueprint, g, render_template
from jinja2 import contextfunction, Markup
from markdown import markdown as md

from .slughifi import slughifi


filters = Blueprint('filters', __name__)


def silent_none(value):
    """
    Return `None` values as empty strings
    """
    if value is None:
        return ''
    return value


@filters.app_template_global('read_file')
def read_file(path, absolute=False, encoding='utf-8'):
    """
    Read the file at `path`. If `absolute` is True, use absolute path,
    otherwise path is assumed to be relative to Tarbell template root dir.
    """
    site = g.current_site
    if not absolute:
        path = os.path.join(site.path, path)

    try:
        return codecs.open(path, 'r', encoding).read()
    except IOError:
        return None


@filters.app_template_global('render_file')
def render_file(path, absolute=False):
    """
    Render a file with the current context
    """
    site = g.current_site
    if not absolute:
        path = os.path.join(site.path, path)

    return render_template(path, **context)


@filters.app_template_filter('markdown')
def markdown(value):
    """
    Run text through markdown process

    >>> markdown('*test*')
    Markup(u'<p><em>test</em></p>')
    """
    return Markup(md(value))


@filters.app_template_filter('format_date')
def format_date(value, format='%b. %d, %Y', convert_tz=None):
    """
    Format an Excel date.

    >>> format_date(42419.82163)
    'Feb. 19, 2016'
    """
    if isinstance(value, float) or isinstance(value, int):
        seconds = (value - 25569) * 86400.0
        parsed = datetime.datetime.utcfromtimestamp(seconds)
    else:
        parsed = dateutil.parser.parse(value)
    if convert_tz:
        local_zone = dateutil.tz.gettz(convert_tz)
        parsed = parsed.astimezone(tz=local_zone)

    return parsed.strftime(format)


@filters.app_template_filter('pprint_lines')
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

