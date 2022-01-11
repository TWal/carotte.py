#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
# carotte.py by Twal, hbens & more

'''Entry point of the carotte.py DSL'''

import argparse
import importlib.abc
import importlib.util
import re
import sys

try:
    import colored_traceback # type: ignore
    colored_traceback.add_hook(always=True)
except ModuleNotFoundError:
    print("Warning: Install module 'colored_traceback' for better tracebacks", file=sys.stderr)

try:
    import assignhooks # type: ignore
    #assignhooks.instrument.debug = True
    #assignhooks.patch.debug = True
    #assignhooks.transformer.debug = True

    import alt_transformer
    assignhooks.transformer.AssignTransformer.visit_Assign = alt_transformer.visit_Assign
except ModuleNotFoundError:
    print("Warning: Install module 'assignhooks' for better variable names", file=sys.stderr)
    assignhooks = None

import lib_carotte

MIN_PYTHON = (3, 8)
if sys.version_info < MIN_PYTHON:
    print("Python %s.%s or later is required" % MIN_PYTHON, file=sys.stderr)
    sys.exit(1)

def process(module_file: str, output_filename: str = None) -> None:
    '''Process a carotte.py input python file and build its netlist'''
    module_name = module_file.replace("/", ".")
    module_name = re.sub("\\.py$", "", module_name)
    spec = importlib.util.spec_from_file_location(module_name, module_file)
    if spec is None:
        print(f"Could not load file '{module_file}'", file=sys.stderr)
        sys.exit(1)
    assert isinstance(spec.loader, importlib.abc.Loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    lib_carotte.reset()
    if assignhooks is not None:
        assignhooks.patch_module(module)

    module.main() # type: ignore

    netlist = lib_carotte.get_netlist()
    if output_filename is None:
        print(netlist, end='')
    else:
        with open(output_filename, 'w') as f:
            f.write(netlist)

def main() -> None:
    '''Entry point for carotte.py'''
    parser = argparse.ArgumentParser(description='carotte.py DSL')
    parser.add_argument("module_file", nargs=1)
    parser.add_argument('-o', '--output-file', help='Netlist output file')
    args = parser.parse_args()
    process(args.module_file[0], args.output_file)

if __name__ == "__main__":
    main()
