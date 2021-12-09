import os
import json

from collections import OrderedDict
from collections.abc import MutableMapping
from io import BytesIO

from io import StringIO

import configparser

supported_formats = ['ini', 'json']

try:
    import yaml
    supported_formats.append('yaml')
except ImportError:
    yaml = None

try:
    import lxml.etree
    supported_formats.append('xml')
except ImportError:
    pass

try:
    import configobj
    supported_formats.append('conf')
except ImportError:
    configobj = None

try:
    import reconfigure
    import reconfigure.configs
    supported_formats.append('reconf')
except (ImportError, SyntaxError):
    reconfigure = None

try:
    import dns.zone
    supported_formats.append('zone')
except (ImportError, SyntaxError):
    dns = None

version = '0.1-git'


class SortedDict(MutableMapping):
    __slots__ = '_data'

    def __init__(self):
        self._data = {}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(sorted(self._data))

    def __len__(self):
        return len(self._data)


if configobj:
    class StrippedConfigObj(configobj.ConfigObj):

        def write(self, outfile=None, section=None, ordered=False):
            if section is None:
                section = self
                self.initial_comment = ''
                self.final_comment = ''
            if not ordered:
                section.scalars.sort()
                section.sections.sort()
            for entry in (section.scalars + section.sections):
                section.comments[entry] = []
                section.inline_comments[entry] = ''
            if section is self:
                section = None
            return super().write(outfile, section)


class DiffBase:

    def __init__(self, filename, ordered=False, parser=None):
        self.filename = filename
        self.ordered = ordered
        self.parser = parser
        self.pretty = StringIO()
        self.error = None
        if filename != '/dev/null' and os.path.getsize(filename) > 0:
            try:
                self.parse()
            except Exception as exc:
                self.error = repr(exc)

    def parse(self):
        pass

    def readlines(self):
        self.pretty.seek(0)
        return self.pretty.readlines()


class INIDiff(DiffBase):

    def parse(self):
        if self.ordered:
            dicttype = OrderedDict
        else:
            dicttype = SortedDict
            self.config = configparser.RawConfigParser(allow_no_value=True,
                                                       dict_type=dicttype,
                                                       strict=False)
        self.config.read(self.filename)
        self.config.write(self.pretty)


class JSONDiff(DiffBase):

    def parse(self):
        sort_keys = self.ordered is False
        with open(self.filename, encoding='utf-8') as jsonfile:
            self.config = json.load(jsonfile)
            json.dump(self.config, self.pretty,
                      sort_keys=sort_keys, indent=4,
                      separators=(',', ': '))


class YAMLDiff(DiffBase):

    def parse(self):
        with open(self.filename, encoding='utf-8') as yamlfile:
            self.config = yaml.safe_load(yamlfile)
            yaml.safe_dump(self.config, self.pretty, default_flow_style=False,
                           indent=2)


class XMLDiff(DiffBase):

    def parse(self):
        parser = lxml.etree.XMLParser(remove_blank_text=True,
                                      remove_comments=True)
        self.config = lxml.etree.parse(self.filename, parser)
        # via https://stackoverflow.com/a/8387132/1098563
        if not self.ordered:
            for parent in self.config.xpath('//*[./*]'):
                parent[:] = sorted(parent, key=lambda x: x.tag)
        self.pretty = BytesIO()
        self.config.write(self.pretty, pretty_print=True)


class ConfigDiff(DiffBase):

    def parse(self):
        self.config = StrippedConfigObj(self.filename)
        self.pretty = BytesIO()
        self.config.write(self.pretty, ordered=self.ordered)


reconfcls = None


class ReconfigureDiff(DiffBase):

    def parse(self):
        with open(self.filename) as f:
            self.config = self.parser(content=f.read())
            l = self.config.load()
            s = l.save()
            self.pretty.write(s[None])


class ZoneDiff(DiffBase):

    def parse(self):
        self.config = dns.zone.from_file(self.filename, 'example.com')
        self.config.to_file(self.pretty, sorted=not self.ordered)
