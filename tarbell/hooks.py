# -*- coding: utf-8 -*-
hooks = {
    'newproject': [],
    'publish': [],
}

class register_hook(object):
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
