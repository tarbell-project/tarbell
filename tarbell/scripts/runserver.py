# -*- coding: utf-8 -*-

"""
tarbell.scripts.runserver
~~~~~~~~~

Wrapper for Tarbell preview server. Should not be run directly in regular use.
"""

import os
import sys

from tarbell.app import TarbellSite

os.chdir(sys.argv[1])
site = TarbellSite(sys.argv[1])
ip = sys.argv[2]
port = int(sys.argv[3])

# try / except
if __name__ == '__main__':
    site.app.run(ip, port=port)
