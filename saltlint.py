#!/usr/bin/env python

import sys
import re
import salt.config
import salt.loader
from inspect import getargspec
import importlib
from IPython.core.debugger import Tracer

def tabcheck(filename):

  ERRORS = []
  prog = re.compile(r'\t')
  count = 1

  with open(filename) as file:
    for line in file:
      match = prog.match(line)

      if match:
        ERRORS.append(ParseError(filename, count, 'Tab character(s) found'))

      count += 1
  return ERRORS

def trailingwscheck(filename):

  ERRORS = []
  prog = re.compile(r'\s+\n')
  count = 1

  with open(filename) as file:
    for line in file:
      match = prog.search(line)

      if match:
        ERRORS.append(ParseError(filename, count, 'Trailing whitespace found'))

      count += 1
  return ERRORS

def indentcheck(filename):

  ERRORS = []
  previous = 0
  required = 2
  count = 1
  nested = 0
  maximum = False

  with open(filename) as file:
    for line in file:
      current = len(line) - len(line.lstrip())

      if maximum:
        if current > maximum:
          break
        else:
          maximum = False

      if current > previous:
        tabsize = current - previous

        if nested == 1:
          if tabsize != 4:
            ERRORS.append(ParseError(filename, count, 'Four space soft tabs for nested dict not found - %s space tab found' % tabsize))
        elif tabsize not in [0, required]:
          ERRORS.append(ParseError(filename, count, 'Two space soft tabs not found - %s space tab found' % tabsize))

      """ context and default options are nested dicts - need 4 space tabs
          http://docs.saltstack.com/en/latest/topics/troubleshooting/yaml_idiosyncrasies.html """
      match = re.search('context:|defaults:', line)

      if match:
        nested = 1
      else:
        nested = 0

      """ don't check indent of datasets """
      if re.search('dataset:', line):
        maximum = current

      count +=1
      previous = current

    return ERRORS

def slscheck(filename):

  ERRORS = []

  prog = re.compile(r'.*\.')

  __opts__ = salt.config.minion_config('/etc/salt/minion')
  renderers = salt.loader.render(__opts__, {})

  try:
    content = renderers['jinja'](filename)
    data = renderers['yaml'](content)
  except salt.exceptions.SaltRenderError as error:
    ERRORS.append(ParseError(filename, 0, error))
    return ERRORS

  for id, v in data.items():

    if id in ['include', 'exclude']:
      break
    for state, options in v.items():

      match = prog.match(state)
      if match:
        (state, method) = state.split('.')
      else:
        method = options.pop(0)

      try:
        package = importlib.import_module("salt.states.%s" % state)
      except:
        ERRORS.append(ParseError(filename, 0, 'id \'%s\' contains unknown state \'%s\'' % (id, state)))

      try:
        args = getargspec(getattr(package, method)).args
        
        """ extra options not available to getargspec """
        args = args + ['watch', 'watch_in', 'require', 'require_in']
        if state == 'file' and method == 'serialize':
          args.append('formatter')

        for opt in options:
          option = opt.keys()[0]
          if option not in args:
            ERRORS.append(ParseError(filename, 0, '%s state with id \'%s\' contains unknown option \'%s\'' % (state, id, option)))
      except:
        ERRORS.append(ParseError(filename, 0, '%s state with id \'%s\' contains unknown method \'%s\'' % (state, id, method)))

  return ERRORS

def ParseError(filename, line, message):
  return {'filename':filename,'line':line,'message':message}

def run(filename):
  ERRORS = tabcheck(filename)
  if len(ERRORS) == 0:
    ERRORS = [] + trailingwscheck(filename) + indentcheck(filename) + slscheck(filename)
  return ERRORS

if __name__ == '__main__':

  ERRS = []
  for file in sys.argv[1:]:
    ERRS = ERRS + run(file)

  for err in sorted(ERRS, key = lambda e: (e['filename'], e['line'])):
    if err['line'] == 0:
      print "%s - %s" % (err['filename'], err['message'])
    else:
      print "%s:%s - %s" % (err['filename'], err['line'], err['message'])

  if len(ERRS) == 0:
    sys.exit(0)
  else:
    sys.exit(1)
