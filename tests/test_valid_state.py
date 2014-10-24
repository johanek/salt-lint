#!/usr/bin/env python

import sys
sys.path.append('.')

import saltlint
errors = saltlint.run('tests/states/valid_state.sls')

def test_valid_state():
  assert len(errors) == 0
