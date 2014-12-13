# -*- coding: utf-8 -*-
'''
Lint states and sls files
'''
from __future__ import absolute_import

# Import python libs
import logging
from types import NoneType
import re
from voluptuous import *
from inspect import getargspec
import importlib

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


def _getschema(state):

    (module, function) = state.split('.')
    try:
        package = importlib.import_module("salt.states.%s" % module)
    except:
        return False

    try:
        argspec = getargspec(getattr(package, function))
    except e:
      return False

    schema = {
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

    for idx, arg in enumerate(argspec.args):
        if arg not in schema:
            try:
                default = argspec.defaults[idx]
            except:
                default = 'nodefault'
            if type(default) == bool:
                stype = bool
            elif type(default) == NoneType:
                stype = Coerce(str)
            else:
                stype = Coerce(type(default))
            schema[arg] = stype

    return Schema(schema)

def validate_sls(mods, saltenv='base', test=None, queue=False, env=None, **kwargs):

    schema = {}
    ret = []
    data = __salt__['state.show_sls'](mods, saltenv, test, queue, env, kwargs=kwargs)

    # iterate over states
    # TODO: add include, exclude to schema
    #       handle context, defaults better
    prog = re.compile(r'.*\.')
    for id, resource in data.items():
        if id in ['include', 'exclude']:
            break

        # iterate over states
        for module, args in resource.items():

            # Ignore data added by show_{sls,highstate}
            if module in ['__sls__', '__env__']:
                break

            # find state name, i.e. cmd.run
            match = prog.match(module)
            if match:
                state = module
            else:
                state = "%s.%s" % (module, args.pop(0))

            # check function exists in schema
            if state not in schema:
                schema[state] =  _getschema(state)
                if schema[state] == False:
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

    if len(ret) > 0:
        __context__['retcode'] = 1
    return ret
