#!/usr/bin/env python

import sys
sys.path.append('.')

import saltlint
errors = saltlint.run('tests/states/tab_characters.sls')

def test_tabs():
  assert len(errors) == 1

def test_tabs_error():
  assert errors[0]['message'] == 'Tab character(s) found'
