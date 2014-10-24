#!/usr/bin/env python

import sys
sys.path.append('.')

import saltlint
errors = saltlint.indentcheck('tests/states/nested_dict.sls')

def test_indent():
  assert len(errors) == 2

def test_indent_error1():
  assert errors[0]['message'] == 'Four space soft tabs for nested dict not found - 2 space tab found'

def test_indent_error2():
  assert errors[1]['message'] == 'Four space soft tabs for nested dict not found - 2 space tab found'
