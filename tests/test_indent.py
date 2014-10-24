#!/usr/bin/env python

import sys
sys.path.append('.')

import saltlint
errors = saltlint.indentcheck('tests/states/soft_tabs.sls')

def test_indent():
  assert len(errors) == 2

def test_indent_error1():
  assert errors[0]['message'] == 'Two space soft tabs not found - 4 space tab found'

def test_indent_error2():
  assert errors[1]['message'] == 'Two space soft tabs not found - 5 space tab found'
