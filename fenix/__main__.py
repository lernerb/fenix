from __future__ import print_function

import functools
import inspect
import sys
from optparse import OptionParser

from fenix import serializers


def _add_custom(func):
    @functools.wraps(func)
    def wrapper(object):
        if hasattr(object,"d_class") and object.d_class == "frame":
            object = object.f_code
        return func(object)
    return wrapper


inspect.findsource = _add_custom(inspect.findsource)


def main():
    parser = OptionParser(usage="%prog <filename.dump> [options]", description="pydump v%s: post-mortem debugging for Python programs" % serializers.__version__)
    parser.add_option("--pdb",  action="append_const", const="pdb",  dest="debuggers", help="Use builtin pdb or pdb++")
    parser.add_option("--pudb", action="append_const", const="pudb", dest="debuggers", help="Use pudb visual debugger")
    parser.add_option("--ipdb", action="append_const", const="ipdb", dest="debuggers", help="Use ipdb IPython debugger")
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(1)

    if not options.debuggers:
        options.debuggers = ["pdb"]

    for debugger in options.debuggers:
        try:
            dbg = __import__(debugger)
        except ImportError as e:
            print(str(e), file=sys.stderr)
            continue
        else:
            print("Starting %s..." % debugger, file=sys.stderr)
            if debugger == "pudb":
                serializers.debug_dump(args[0], lambda tb: dbg.post_mortem(tb))
            else:
                serializers.debug_dump(args[0])
            break


if __name__ == '__main__':
    main()