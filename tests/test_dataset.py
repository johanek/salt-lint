#!/usr/bin/env python

import sys
sys.path.append('.')

import saltlint
errors = saltlint.run('tests/states/dataset.sls')

def test_indent():
  assert len(errors) == 0
