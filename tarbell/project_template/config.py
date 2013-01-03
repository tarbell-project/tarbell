"""
Google doc configuration. If not provided, no Google doc will be used.
"""
{% if spreadsheet_key %}
GOOGLE_DOC = {
    'key': "{{ spreadsheet_key }}",
    'account': "<gmail address>",
    'password': "<password>",
}
{% else %}
# GOOGLE_DOC = {
    # 'key': "<spreadsheet key>",
    # 'account': "<gmail address>",
    # 'password': "<password>",
# }
{% endif %}


"""
Set default context. These variables will be globally available to the template.
"""
# DEFAULT_CONTEXT = {
#     'ad_path': '',
#     'analytics_path': '',
# }


"""
Root URL project will appear at (e.g. http://mydomain.tld/{{ url_root }})
"""
# URL_ROOT = '{{ project_name }}'


"""
Don't render to static HTML.
"""
# DONT_PUBLISH = False

"""
Uncomment the following lines to provide this configuration file as a Flask
blueprint.
"""
# from flask import Blueprint
# blueprint = Blueprint('{{ project_name }}', __name__)

"""
Example use of flask blueprint to add a template filter.
"""
# @blueprint.app_template_filter('example_filter')
# def example_filter(text):
#    return text + ' ...suffix.'
