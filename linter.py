#!/usr/bin/env python

import sys
import yaml
import re
import salt.config
import salt.loader
from inspect import getargspec
import importlib

def tabcheck(filename):
	
  prog = re.compile(r'\t')
  count = 1

  with open(filename) as file:
    for line in file:
      match = prog.match(line)

      if match:
        ParseError(filename, count, 'Tab character(s) found')

      count += 1

def indentcheck(filename):

  previous = 0
  required = 2
  count = 0
  nested = 0

  with open(filename) as file:
    for line in file:
      current = len(line) - len(line.lstrip())

      if current > previous:
        tabsize = current - previous

        if nested == 1:
          if tabsize != 4:
            ParseError(filename, count, 'Four space soft tabs for nested dict not found - %s space tab found' % tabsize)

        if tabsize not in [0, required]:
          ParseError(filename, count, 'Two space soft tabs not found - %s space tab found' % tabsize)

      """ context and default options are nested dicts - need 4 space tabs
          http://docs.saltstack.com/en/latest/topics/troubleshooting/yaml_idiosyncrasies.html """
      match = re.search('context|defaults:', line)

      if match:
        nested = 1
      else:
        nested = 0

      count +=1
      previous = current


def yamlcheck(filename):

  with open(filename) as file:
    try:
      yaml.load(file)
      return 0
    except (yaml.parser.ParserError, yaml.scanner.ScannerError) as error:
    	if hasattr(error, 'problem_mark'):
    		mark = error.problem_mark
        ParseError(filename, mark.line+1, 'YAML Parsing error at column %s' % (mark.column+1))
        return 1

    except:
      ParseError(filename, 0, 'Unexpected Error parsing YAML')
      return 2


def slscheck(filename):
  content = open(filename).read()
  __opts__ = salt.config.minion_config('minion.conf')
  renderers = salt.loader.render(__opts__, {})
  data = renderers['yaml'](content)

  for id, v in data.items():
    for state, options in v.items():
      package = importlib.import_module("salt.states.%s" % state)
      method = options[0]

      try:
        args = getargspec(getattr(package, method)).args
        for opt in options[1:]:
          option = opt.keys()[0]
          if option not in args:
            ParseError(filename, 0, '%s state with id \'%s\' calls unknown option %s' % (state, id, option ))
      except:
        ParseError(filename, 0, '%s state with id \'%s\' calls unknown method %s' % (state, id, method))


def ParseError(filename, line, message):
  ERRORS.append({'filename':filename,'line':line,'message':message})

if __name__ == '__main__':

  ERRORS = []

  tabcheck(sys.argv[1])
  indentcheck(sys.argv[1])
  #yamlcheck(sys.argv[1])
  slscheck(sys.argv[1])

  for err in sorted(ERRORS, key = lambda e: (e['filename'], e['line'])):
    if err['line'] == 0:
      print "%s - %s" % (err['filename'], err['message'])
    else:
      print "%s:%s - %s" % (err['filename'], err['line'], err['message'])

  if len(ERRORS) == 0:
    sys.exit(0)
  else:
    sys.exit(1)
