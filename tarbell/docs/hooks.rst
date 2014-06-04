=====
Hooks
=====

Tarbell hooks allow project and base template developers to take actions during Tarbell project creation, projection installation, generation, and publishing.

To define a hook, edit ``tarbell_config.py`` or ``blueprint.py``:

.. code-block:: python

  from tarbell.hooks import register_hook

  @register_hook("newproject")
  def create_tickets(site, git):
      # ... code to create tickets on service of your choice

Here is a more advanced hook from the Bootstrap base template that prompts the user to create a new repo
for their project on Github after project creation:

.. code-block:: python

  import requests
  import getpass

  from clint.textui import puts, colored
  from tarbell.hooks import register_hook

  @register_hook('newproject')
  def create_repo(site, git):
      create = raw_input("Want to create a Github repo for this project [Y/n]? ")
      if create and not create.lower() == "y":
          return puts("Not creating Github repo...")

      name = site.project.NAME
      user = raw_input("What is your Github username? ")
      password = getpass.getpass("What is your Github password? ")
      headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
      data = {'name': name, 'has_issues': True, 'has_wiki': True}
      resp = requests.post('https://api.github.com/user/repos', auth=(user, password), headers=headers, data=json.dumps(data))
      puts("Created {0}".format(colored.green("https://github.com/{0}/{1}".format(user, name))))
      clone_url = resp.json().get("clone_url")
      puts(git.remote.add("origin", "git@github.com:{0}/{1}.git".format(user,name)))
      puts(git.push("origin", "master"))

      create = raw_input("Would you like to create some default issues [Y/n]? ")
      if create and not create.lower() == "y":
          return puts("Not creating default issues")

      for title, description in ISSUES:
          puts("Creating {0}".format(colored.yellow(title)))
          data = {'title': title, 'body': description}
          resp = requests.post('https://api.github.com/repos/{0}/{1}/issues'.format(user, name), auth=(user, password), headers=headers, data=json.dumps(data))

Use the publish hook to update the Facebook cache:

.. code-block:: python

  import urllib

  from clint.textui import colored, puts
  from tarbell.hooks import register_hook

  def _ping_facebook(url):
      url = "{0}?fbrefresh=CANBEANYTHING".format(url)
      fb_url = "http://developers.facebook.com/tools/debug/og/object?q={0}".format(urllib.quote_plus(url))
      urllib.urlopen(fb_url)
      puts("Pinging {0}".format(colored.yellow(fb_url)))


  @register_hook('publish')
  def update_facebook(site, s3):
      for name, path in s3.find_file_paths():
          if name.endswith(".html"):
              _ping_facebook("http://{0}/{1}".format(s3.bucket, name))


Finally, here's a hook from a project's `tarbell_config.py` that publishes special social media stub
pages for each row in a worksheet. This allows individual items to be shared from a single-page 
listicle app:

.. code-block:: python

  import jinja2

  from blueprint import _ping_facebook
  from boto.s3.key import Key
  from clint.textui import puts, colored
  from tarbell.hooks import register_hook

  @register_hook('publish')
  def create_social_stubs(site, s3):
      loader = jinja2.FileSystemLoader('./')
      env = jinja2.Environment(loader=loader)
      template = env.get_template('_fb_template.html')
      data = site.get_context_from_gdoc()

      for row in data.get("list_items", []):
          k = Key(s3.connection)
          k.key = '{0}/rows/{1}.html'.format(s3.bucket.path, row['id'])
          redirect = 'http://{0}/rows/#{1}'.format(s3.bucket, row['id'])
          puts('Redirect {0} to {1}'.format(colored.yellow(k.key), colored.yellow(redirect)))
          output = template.render(bucket=s3.bucket,**row)
          options = {
              'Content-Type': 'text/html',
          }
          k.set_contents_from_string(output, options)
          k.set_acl('public-read')
          url = "http://{0}/{1}".format(s3.bucket.root, k.key)
          _ping_facebook(url)

Here's the `_fb_template` referenced above:

.. code-block:: html

  <html>

  <head>
    <script>
      document.location = "http://{{ bucket }}/#{{ id }}";
    </script>

    <meta property="og:url" content="http://{{ bucket }}/rows/{{ id }}.html" />
    <meta property="og:title" content="Great moments in history: {{ heading }}" />
    <meta property="og:description" content="{{ og }}" />
    <meta property="og:image" content="http://{{ bucket }}/img/{{ img }}" />
  </head>

  <body></body>

  </html>
