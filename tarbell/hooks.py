# -*- coding: utf-8 -*-
hooks = {
    'newproject': [],        # (site)
    'generate': [],          # (site, dir, extra_context)
    'publish': [],           # (site, s3)
    'install': [],           # (site, project)
    'preview': [],           # (site)
    'server_start': [],      # (site)
    'server_stop': [],       # (site)
}


class register_hook(object):
    """Register hook with @register_hook("EVENT") where EVENT is "newproject" etc"""
    def __init__(self, event):
        self.event = event

    def __call__(self, f):
        # Avoid weird duplication
        names = ['{0}.{1}'.format(func.__module__, func.func_name) for func in hooks[self.event]]
        if '{0}.{1}'.format(f.__module__, f.func_name) not in names:
            hooks[self.event].append(f)
        return f
