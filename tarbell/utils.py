import sys
from clint.textui import colored

def list_get(l, idx, default=None):
    """Get from a list with an optional default value."""
    try:
        if l[idx]:
            return l[idx]
        else:
            return default
    except IndexError:
        return default


def black(s):
    """Black text."""
    #if settings.allow_black_foreground:
        #return colored.black(s)
    #else:
    return s.encode('utf-8')


def split_sentences(s):
    """Split sentences for formatting."""
    sentences = []
    for index, sentence in enumerate(s.split('. ')):
        pad = ''
        if index > 0:
            pad = ' ' * 39
        if sentence.endswith('.'):
            sentence = sentence[:-1]
        sentences.append('%s %s.' % (pad, sentence.strip()))
    return "\n".join(sentences)


def show_error(msg):
    """Displays error message."""
    sys.stdout.flush()
    sys.stderr.write("{0}: {1}".format(colored.red("Error"), msg + '\n'))

