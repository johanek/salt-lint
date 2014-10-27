#!/usr/bin/env python

import sys
sys.path.append('.')

import saltlint
errors = saltlint.run('tests/states/trailing_whitespace.sls')

def test_trailing_whitespace():
  assert len(errors) == 1

def test_trailing_whitespace_error():
  assert errors[0]['message'] == 'Trailing whitespace found'
