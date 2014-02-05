cfgdiff -- `diff(1)` all your configuration files
=================================================

Why?
----
Ever tried comparing MySQL's `my.cnf` from a Debian and a Gentoo machine
with `diff(1)` without going crazy?

`diff(1)` is an awesome tool, you use it (or similar implementations
like `git diff`, `svn diff` etc) every day when dealing with code.
But configuration files aren't code. Indentation often does not matter
(yeah, there is `diff -w` and yeah, people use YAML for configs), order
of settings does not matter and comments are just beautiful noise.

How?
----
`cfgdiff` will try to parse your configuration files, fetching all the
relevant keys and values from them and then pretty-printing them in the
original format. These results are then diffed and the diff is shown to
you.

What?
-----
`cfgdiff` currently supports the following formats:

- INI using Python's [ConfigParser](http://docs.python.org/library/configparser.html) library
- JSON using Python's [JSON](http://docs.python.org/library/json.html) library
- YAML if the Python [YAML](http://pyyaml.org/) library is installed
- XML if the Python [lxml](http://lxml.de/) library is installed
