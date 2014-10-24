#!/usr/bin/env python

import sys
sys.path.append('.')

import saltlint
errors = saltlint.run('tests/states/invalid_yaml.sls')

def test_invalid_yaml():
  assert len(errors) == 1
