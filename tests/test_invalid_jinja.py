#!/usr/bin/env python

import sys
sys.path.append('.')

import saltlint
errors = saltlint.run('tests/states/invalid_jinja.sls')

def test_invalid_yaml():
  assert len(errors) == 1
