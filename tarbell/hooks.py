# -*- coding: utf-8 -*-
hooks = {
    'newproject': [],        # (site)
    'generate': [],          # (site, tempdir)
    'publish': [],           # (site, s3)
    'install': [],           # (site, project)
}


class register_hook(object):
    """Register hook with @register_hook("EVENT") where event is "newproject" etc"""
    def __init__(self, event):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        print "Inside __init__()"
        self.event = event

    def __call__(self, f):
        if f not in hooks[self.event]:
            hooks[self.event].append(f)
        return f
