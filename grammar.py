#!/usr/bin/env python
"""

Usage:
        grammar.py file.grammar > grammar.yaml

"""
import re
import sys
from warnings import warn
import pprint

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

def y(o):
    print yaml.dump(o, default_flow_style=False)
    return o

sys.path.insert(0, '..')

from cdent.grammar import *

class GrammarModule():
    def __init__(self, paths):
        dict = {}
        for path in paths:
            dict.update(yaml.load(file(path)))
        self.grammar = {}
        regexps = {}
        atoms = yaml.load(file('grammar/atoms.yaml'))
        for k in atoms:
            v = atoms[k]
            if v[0] != '/':
                raise Exception("bad atom")
            atoms[k] = v[1:-1]
        for k in dict:
            v = dict[k]
            t = v.__class__.__name__
            if t == 'str' and v[0] == '/':
                regexps[k] = v[1:-1]
            else:
                self.grammar[k] = v
        def f(m):
            n = m.groups()[0]
            if n in atoms:
                return atoms[n]
            if n in regexps:
                return regexps[n]
            raise Exception("'%s' is not defined in the grammar" % n)
        for k in regexps:
            v = regexps[k]
            while True:
                v2 = re.sub(r'\$<?(\w+)>?', f, v)
                if v2 == v:
                    break
                v = v2
            self.grammar[k] = Re({'_': v})
#         y(self.grammar)
        for k in self.grammar:
            self.grammar[k] = self.parse(self.grammar[k])

    def parse(self, node):
#         print "parse> " + repr(node)
        t = node.__class__.__name__
        if t == 'str':
            return self.parse_str(node)
        elif t == 'list':
            return self.parse_list(node)
        elif t == 'dict':
            return self.parse_dict(node)
        else:
            return node

    def parse_dict(self, dict):
#         print "parse_dict> " + repr(dict)
        obj = self.parse(dict['_'])
        if 'x' in dict:
            setattr(obj, 'x', dict['x'])
        return obj

    def parse_list(self, list):
#         print "parse_list> " + repr(list)
        new = []
        for e in list:
            new.append(self.parse(e))
        return All({'_': new})

    def parse_str(self, str):
#         print "parse_str> " + repr(str)
        d = {}
        if str == 'indent':
            return Indent({})
        if str == 'undent':
            return Undent({})
        if str[-1] in '*+?':
            d['x'] = str[-1]
            str = str[0:-1]
        if str[-1] == '!':
            str = str[0:-1]
            rule = self.parse(str)
            rule.__dict__['!'] = True
            return rule
        elif str[0] == '(':
            str = str[1:-1]
            list = []
            a = str.split('|')
            for e in a:
                list.append(self.parse(e))
            d['_'] = list
            return Any(d)
        elif re.match(r'^\w+$', str):
            d['_'] = str
            return Rule(d)
        else:
            raise Exception("Failed to parse '%s'" % str)

    def generate_module(self, lang):
        Lang = lang[0].upper() + lang[1:]
        data = pprint.pformat(self.grammar, indent=2)

        module = """\
\"\"\"
C'Dent %(Lang)s parser grammar module.
\"\"\"

from cdent.grammar import *

class Grammar():
    def __init__(self):
        self.__dict__.update(
%(data)s
)
""" % locals()
 
        return module

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception(__doc__)
    grammar_file = sys.argv[1]
    print GrammarModule(grammar_file).generate_yaml()
