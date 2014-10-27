#!/usr/bin/env python

import sys
import re
import salt.config
import salt.loader
from inspect import getargspec
import importlib
from IPython.core.debugger import Tracer

def tabcheck(content, filename):

  ERRORS = []
  prog = re.compile(r'\t')

  for index, line in enumerate(content.split("\n")):
    if prog.search(line):
      ERRORS.append(ParseError(filename, index + 1, 'Tab character(s) found'))
  return ERRORS

def trailingwscheck(content, filename):

  ERRORS = []
  prog = re.compile(r'\s+$')

  for index, line in enumerate(content.split("\n")):
    if prog.search(line):
      ERRORS.append(ParseError(filename, index + 1, 'Trailing whitespace found'))
  return ERRORS

def indentcheck(content, filename):

  ERRORS = []
  previous = 0
  required = 2
  nested = 0
  maximum = False

  for index, line in enumerate(content.split("\n")):

    """ check indent of line """
    current = len(line) - len(line.lstrip())

    """ don't check indent of datasets """
    if maximum:
      if current > maximum:
        break
      else:
        maximum = False
    if re.search('dataset:', line):
      maximum = current

    """ run checks if indented compared to previous line """
    if current > previous:
      tabsize = current - previous

      if nested == 1:
        if tabsize != 4:
          ERRORS.append(ParseError(filename, index + 1, 'Four space soft tabs for nested dict not found - %s space tab found' % tabsize))
      elif tabsize not in [0, required]:
        ERRORS.append(ParseError(filename, index + 1, 'Two space soft tabs not found - %s space tab found' % tabsize))

    """ context and default options are nested dicts - need 4 space tabs
        http://docs.saltstack.com/en/latest/topics/troubleshooting/yaml_idiosyncrasies.html """
    if re.search('context:|defaults:', line):
      nested = 1
    else:
      nested = 0

    previous = current
  return ERRORS

def jinjacheck(filename):
  ERRORS = []
  content = ""
  renderers = getrenderers()

  try:
    content = renderers['jinja'](filename).read()
  except salt.exceptions.SaltRenderError as error:
    ERRORS.append(ParseError(filename, 0, error))

  return content, ERRORS

def slscheck(content, filename):

  ERRORS = []

  prog = re.compile(r'.*\.')
  renderers = getrenderers()

  try:
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

def getrenderers():
  __opts__ = salt.config.minion_config('/etc/salt/minion')
  renderers = salt.loader.render(__opts__, {})
  return renderers

def ParseError(filename, line, message):
  return {'filename':filename,'line':line,'message':message}

def run(filename):
  content, ERRORS = jinjacheck(filename)
  ERRORS = ERRORS + tabcheck(content, filename)
  if len(ERRORS) == 0:
    ERRORS = ERRORS + trailingwscheck(content,filename) + indentcheck(content, filename) + slscheck(content, filename)
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
