#!/usr/bin/env python

import sys
sys.path.append('.')

import saltlint
errors = saltlint.run('tests/states/include.sls')

def test_include():
  assert len(errors) == 0
