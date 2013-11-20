import gzip
import mimetypes
import os
import os.path
import re
import shutil
import tempfile

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from clint.textui import puts
from urllib import quote_plus
from urllib2 import urlopen

excludes = r'|'.join([r'.*\.git$'])


class S3Sync:
    def __init__(self, directory, bucket, key_id, key, force=False):
        self.force = force
        self.connection = S3Connection(key_id, key)
        self.bucketname, self.prefix = bucket[5:].split('/', 1)
        self.bucket = self.connection.get_bucket(self.bucketname)
        self.directory = directory.rstrip('/')

    def deploy_to_s3(self):
        """
        Deploy a directory to an s3 bucket.
        """
        self.tempdir = tempfile.mkdtemp('s3deploy')

        for keyname, absolute_path in self.find_file_paths():
            self.s3_upload(keyname, absolute_path)

        shutil.rmtree(self.tempdir, True)
        return True

    def s3_upload(self, keyname, absolute_path):
        """
        Upload a file to s3
        """
        mimetype = mimetypes.guess_type(absolute_path)
        options = {'Content-Type': mimetype[0]}

        if mimetype[0] is not None and mimetype[0].startswith('text/'):
            upload = open(absolute_path)
            options['Content-Encoding'] = 'gzip'
            key_parts = keyname.split('/')
            filename = key_parts.pop()
            temp_path = os.path.join(self.tempdir, filename)
            gzfile = gzip.open(temp_path, 'wb')
            gzfile.write(upload.read())
            gzfile.close()
            absolute_path = temp_path

        size = os.path.getsize(absolute_path)
        key = "{0}/{1}".format(self.prefix, keyname)
        existing = self.bucket.get_key(key)

        if self.force or not existing or (existing.size != size):
            k = Key(self.bucket)
            k.key = key
            puts("Uploading {0}/{1}".format(self.bucketname, k.key))
            k.set_contents_from_filename(absolute_path, options, policy='public-read')

            if key.endswith('.html'):
                param = "http://{0}/{1}?fbrefresh=CANBEANYTHING".format(self.bucketname, key)
                puts("Refreshing Facebook info for: {0}".format(param))
                fb_url = "http://developers.facebook.com/tools/debug/og/object?q={0}".format(quote_plus(param))
                urlopen(fb_url)
        else:
            puts("Skipping {0}, file sizes match".format(keyname))


    def find_file_paths(self):
        """
        A generator function that recursively finds all files in the upload directory.
        """
        paths = []
        for root, dirs, files in os.walk(self.directory, topdown=True):
            dirs[:] = [d for d in dirs if not re.match(excludes, d)]
            rel_path = os.path.relpath(root, self.directory)

            for f in files:
                if f.startswith('.'):
                    continue
                if rel_path == '.':
                    paths.append((f, os.path.join(root, f)))
                else:
                    paths.append((os.path.join(rel_path, f), os.path.join(root, f)))

        return paths
