# SPDX-License-Identifier: CC0-1.0
# carotte.py by TWal, hbens & more

from lib_carotte import *

# You are encouraged to split your project in several modules!
# Here is how to do it:

from tutorial.utils import full_adder # import the full_adder function from utils.py

def main() -> None:
    a = Input(1)
    b = Input(1)
    c = Input(1)
    (result, out_carry) = full_adder(a, b, c)
    result.set_as_output("r")
    out_carry.set_as_output("out_c")

# Expected output:
# INPUT a, b, c
# OUTPUT r, out_c
# VAR a, b, c, _l_3, r, _l_5, _l_6, out_c
# IN
# _l_3 = XOR a b
# r = XOR _l_3 c
# _l_5 = AND _l_3 c
# _l_6 = AND a b
# out_c = OR _l_5 _l_6
