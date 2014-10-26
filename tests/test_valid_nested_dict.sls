#!/usr/bin/env python

import sys
sys.path.append('.')

import saltlint
errors = saltlint.run('tests/states/valid_nested_dict.sls')

def test_indent():
  assert len(errors) == 0
