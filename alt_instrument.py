# SPDX-License-Identifier: MIT
# Copyright (c) 2021 patgolez10, sinavir
"""asignhooks patch to instrument only modules from specific paths"""

import os.path

import assignhooks

origin_import = __import__

path = []


def custom_import(name, *args, **kwargs):
    module = origin_import(name, *args, **kwargs)
    if not hasattr(module, "__file__") or not _is_in_path(module.__file__):
        return module
    try:
        assignhooks.patch.patch_module(
            module, trans=assignhooks.transformer.AssignTransformer
        )
    except Exception as e:
        print(e)
        return module
    return module


def _is_in_path(p):
    """
    test if one membre of `path` is a prefix of `p`
    """
    p = os.path.normpath(p)
    for i in path:
        if i == os.path.commonpath([i, p]):
            return True
    return False


def start():
    __builtins__.update(**dict(__import__=custom_import))


def stop():
    __builtins__.update(**dict(__import__=origin_import))
