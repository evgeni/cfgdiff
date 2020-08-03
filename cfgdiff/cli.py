#!/usr/bin/env python

from __future__ import print_function

import argparse
import difflib
import os
import sys

from . import __version__
from .cfgdiff import (
    ConfigDiff, INIDiff, JSONDiff, ReconfigureDiff, XMLDiff,
    YAMLDiff, ZoneDiff, reconfigure, supported_formats
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument("-c", action="store_true", default=False,
                        help='Produce a context format diff (default)')
    parser.add_argument("-u", action="store_true", default=False,
                        help='Produce a unified format diff')
    hlp = 'Produce HTML side by side diff (can use -c and -l in conjunction)'
    parser.add_argument("-m", action="store_true", default=False, help=hlp)
    parser.add_argument("-n", action="store_true", default=False,
                        help='Produce a ndiff format diff')
    hlp = 'Set number of context lines (default: %(default)s)'
    parser.add_argument("-l", "--lines", type=int, default=3,
                        help=hlp)
    parser.add_argument('-i', '--input-format', dest='inputformat', default='ini',
                        choices=supported_formats,
                        help='parse input as %s (default: %%(default)s)' %
                        '/'.join(supported_formats))
    parser.add_argument('-r', '--recursive', dest='recursive', action='store_true',
                        default=False,
                        help='recursively compare any subdirectories found')
    parser.add_argument('-N', '--new-file', dest='newfile', action="store_true",
                        default=False, help='treat absent files as empty')
    parser.add_argument('-O', '--ordered-input', dest='ordered',
                        action="store_true",
                        default=False,
                        help='do not change order of options in the input')
    if reconfigure:
        hlp = 'Use this reconfigure.configs class (default: %(default)s)'
        parser.add_argument('-R', '--reconf-class', dest='reconfclass',
                            default='SambaConfig',
                            help=hlp)
    parser.add_argument('fromfile')
    parser.add_argument('tofile')
    options = parser.parse_args()

    n = options.lines

    parsercls = None

    if options.inputformat == 'ini':
        cls = INIDiff
    elif options.inputformat == 'json':
        cls = JSONDiff
    elif options.inputformat == 'yaml':
        cls = YAMLDiff
    elif options.inputformat == 'xml':
        cls = XMLDiff
    elif options.inputformat == 'conf':
        cls = ConfigDiff
    elif options.inputformat == 'reconf':
        exec("from reconfigure.configs import %s as parsercls" % options.reconfclass)
        cls = ReconfigureDiff
    elif options.inputformat == 'zone':
        cls = ZoneDiff

    fromlist = []
    tolist = []
    if options.recursive and os.path.isdir(options.fromfile) and os.path.isdir(options.tofile):
        for root, _, files in os.walk(options.fromfile):
            for f in files:
                x = os.path.join(root, f)
                fromlist.append(x)
                y = os.path.join(options.tofile, os.path.relpath(x, options.fromfile))
                if os.path.exists(y):
                    tolist.append(y)
                else:
                    tolist.append('/dev/null')
        for root, _, files in os.walk(options.tofile):
            for f in files:
                x = os.path.join(root, f)
                if x not in tolist:
                    tolist.append(x)
                    y = os.path.join(options.fromfile, os.path.relpath(x, options.tofile))
                    if os.path.exists(y):
                        fromlist.append(y)
                    else:
                        fromlist.append('/dev/null')
    elif options.recursive and (os.path.isdir(options.fromfile) or os.path.isdir(options.tofile)):
        print("cannot compare folders and files")
        sys.exit(2)
    else:
        fromlist.append(options.fromfile)
        tolist.append(options.tofile)

    rc = 0

    # Print HTML header if HTML + recursive mode :
    header = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
              "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

    <html>

    <head>
        <meta http-equiv="Content-Type"
              content="text/html; charset=ISO-8859-1" />
        <title></title>
        <style type="text/css">
            table.diff {font-family:Courier; border:medium;}
            .diff_header {background-color:#e0e0e0}
            td.diff_header {text-align:right}
            .diff_next {background-color:#c0c0c0}
            .diff_add {background-color:#aaffaa}
            .diff_chg {background-color:#ffff77}
            .diff_sub {background-color:#ffaaaa}
        </style>
    </head>

    <body>
    """

    if options.m and options.recursive:
        sys.stdout.write(header)

    for fromfile, tofile in zip(fromlist, tolist):
        if '/dev/null' in (fromfile, tofile) and not options.newfile:
            rc = 1
            if fromfile != '/dev/null':
                x = os.path.relpath(fromfile, options.fromfile)
                print('Only in %s: %s' % (options.fromfile, x))
            else:
                x = os.path.relpath(tofile, options.tofile)
                print('Only in %s: %s' % (options.tofile, x))
            continue

        fromini = cls(fromfile, options.ordered, parsercls)
        toini = cls(tofile, options.ordered, parsercls)

        if fromini.error:
            print("%s could not be parsed as a %s file:" % (fromfile, options.inputformat))
            print(" %s" % (fromini.error))
            print("It will be interpreted as an empty file.")
        if toini.error:
            print("%s could not be parsed as a %s file:" % (tofile, options.inputformat))
            print(" %s" % (toini.error))
            print("It will be interpreted as an empty file.")

        fromlines = fromini.readlines()
        tolines = toini.readlines()

        if options.u:
            diff = difflib.unified_diff(fromlines, tolines, fromfile, tofile, n=n)
        elif options.n:
            diff = difflib.ndiff(fromlines, tolines)
        elif options.m and not options.recursive:
            diff = difflib.HtmlDiff().make_file(fromlines, tolines, fromfile,
                                                tofile, context=options.c,
                                                numlines=n)
        elif options.m and options.recursive:
            diff = difflib.HtmlDiff().make_table(fromlines, tolines, fromfile,
                                                 tofile, context=options.c,
                                                 numlines=n)
            diff += "<br/>"
        else:
            diff = difflib.context_diff(fromlines, tolines, fromfile, tofile, n=n)

        for line in diff:
            sys.stdout.write(line)
            rc = 1

    # Print HTML footer if HTML + recursive mode :
    footer = """
        <table class="diff" summary="Legends">
        <tr> <th colspan="2"> Legends </th> </tr>
        <tr> <td> <table border="" summary="Colors">
                      <tr><th> Colors </th> </tr>
                      <tr><td class="diff_add">&nbsp;Added&nbsp;</td></tr>
                      <tr><td class="diff_chg">Changed</td> </tr>
                      <tr><td class="diff_sub">Deleted</td> </tr>
                  </table></td>
             <td> <table border="" summary="Links">
                      <tr><th colspan="2"> Links </th> </tr>
                      <tr><td>(f)irst change</td> </tr>
                      <tr><td>(n)ext change</td> </tr>
                      <tr><td>(t)op</td> </tr>
                  </table></td> </tr>
        </table>

        </body>
    </html>
    """
    if options.m and options.recursive:
        sys.stdout.write(footer)

    sys.exit(rc)


if __name__ == '__main__':
    main()
