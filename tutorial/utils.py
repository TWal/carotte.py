# SPDX-License-Identifier: CC0-1.0
# carotte.py by TWal, hbens & more

'''Utility file to be demonstrated with 4_modules.py'''

from lib_carotte import *

def full_adder(a: Variable, b: Variable, c: Variable) -> typing.Tuple[Variable, Variable]:
    tmp = a ^ b
    return (tmp ^ c, (tmp & c) | (a & b))
