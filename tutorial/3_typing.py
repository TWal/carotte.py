# SPDX-License-Identifier: CC0-1.0
# carotte.py by Twal, hbens & more

from lib_carotte import *

# Carotte.py is statically typed using the PEP 484 <https://www.python.org/dev/peps/pep-0484/>
# You can check the typing of a file using mypy <http://mypy-lang.org/>

# You can declare the argument and return type like this:
def full_adder(a: Variable, b: Variable, c: Variable) -> typing.Tuple[Variable, Variable]:
    tmp = a ^ b
    return (tmp ^ c, (tmp & c) | (a & b))

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
# VAR a, b, c, tmp, r, _l_5, _l_6, out_c
# IN
# tmp = XOR a b
# r = XOR tmp c
# _l_5 = AND tmp c
# _l_6 = AND a b
# out_c = OR _l_5 _l_6
