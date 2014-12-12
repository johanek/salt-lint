# -*- coding: utf-8 -*-
'''
Lint states and sls files
'''
from __future__ import absolute_import

# Import python libs
import os
import json
import copy
import shutil
import time
import logging
import tarfile
import datetime
import tempfile
from types import NoneType
import re
from voluptuous import *

# Import salt libs
import salt.config
import salt.utils
import salt.state
import salt.payload
from salt.ext.six import string_types
from salt.exceptions import SaltInvocationError

__outputter__ = {
    'validate_sls': 'highstate',
}

log = logging.getLogger(__name__)

def _schema():
    statemods = salt.loader.states(__opts__, __salt__)
    argspecs = salt.utils.argspec_report(statemods)

    specialargs = {
        'name': Coerce(str),
        'names': list,
        'check_cmd': str,
        'listen': list,
        'listen_in': list,
        'onchanges': list,
        'onchanges_in': list,
        'onfail': list,
        'onfail_in': list,
        'onlyif': Coerce(str),
        'order': int,
        'prereq': list,
        'prereq_in': list,
        'require': list,
        'require_in': list,
        'unless': Coerce(str),
        'use': list,
        'watch': list,
        'watch_in': list,
        'formatter': str
    }

    # define voluptuous schema
    schema = {}
    for state, specs in argspecs.iteritems():
        s = specialargs.copy()
        for idx, arg in enumerate(specs['args']):

            # Don't overwrite args from specialargs
            if arg in s:
              break

            try:
                default = specs['defaults'][idx]
            except:
                default = 'nodefault'
            if type(default) == bool:
                stype = bool
            elif type(default) == NoneType:
                stype = Coerce(str)
            else:
                stype = Coerce(type(default))
            s[arg] = stype
        schema[state] = Schema(s)

    return schema


def validate_sls(mods, saltenv='base', test=None, queue=False, env=None, **kwargs):

    schema = _schema()
    data = __salt__['state.show_sls'](mods, saltenv, test, queue, env, kwargs=kwargs)
    ret = []

    # iterate over states
    # TODO: add include, exclude to schema
    #       handle context, defaults better
    prog = re.compile(r'.*\.')
    for id, resource in data.items():
        if id in ['include', 'exclude']:
            break

        # iterate over states
        for module, args in resource.items():

            if module in ['__sls__', '__env__']:
                break

            # find state name, i.e. cmd.run
            match = prog.match(module)
            if match:
                state = module
            else:
                state = "%s.%s" % (module, args.pop(0))

            # check function exists in scema
            if state not in schema:
                ret.append("%s: %s not part of schema" % (file, state))
                break

            # iterate over arguments to make sure they're valid according to our schema
            for arg in args:
                if arg.iterkeys().next() in [ 'context', 'defaults' ]:
                    break
                try:
                    schema[state](arg)
                except Exception as e:
                    ret.append("%s %s: Got %s for %s but %s" % (id, state, arg.itervalues().next(), arg.iterkeys().next(), e.msg))

    return ret
