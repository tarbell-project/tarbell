=====
Hooks
=====

Tarbell hooks allow project and blueprint developers to take actions during Tarbell project creation, project installation, generation, and publishing.

To define a hook, edit ``tarbell_config.py`` or ``blueprint.py``:

.. code-block:: python

  from tarbell.hooks import register_hook

  @register_hook("newproject")
  def create_tickets(site, git):
      # ... code to create tickets on service of your choice

Here is a more advanced hook from the Bootstrap blueprint that prompts the user to create a new repo
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

      name = site.project.DEFAULT_CONTEXT.get("name")
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

