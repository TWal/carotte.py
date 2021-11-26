# SPDX-License-Identifier: CC0-1.0
# carotte.py by TWal, hbens & more

# The functions needed to use carotte.py are in the `lib_carotte` module, so we import them
from lib_carotte import *

# And we can define our circuit in the `main` function
def main():
    # We declare input variables using the Input class. It takes as argument the bus size of this variable
    a = Input(1)
    b = Input(1)
    c = Input(1)
    d = Input(8)

    # We can do logical operations like this, using full names:
    e1 = And(a, b)
    e2 = Nand(a, b)
    e3 = Or(a, b)
    e4 = Xor(a, b)
    e5 = Mux(c, a, b)
    e6 = Not(a)
    e7 = Reg(a)
    e8 = Constant("0010")

    # Or using operators
    f1 = a & b # And
    # No operator for Nand
    f3 = a | b # Or
    f4 = a ^ b # Xor
    # No operator for Mux
    f6 = ~a # Not
    # No operator for Reg
    # No operator for Constant

    # We can do complex expressions without naming intermediate expressions
    g = (a | b) & c

    # If a variable is an output, we can state it like this (we have to give it an explicit name as argument):
    g.set_as_output("g")

    # Operation on buses work like this:
    h1 = Select(2, d) # Selection of the third bit of d
    h2 = d[2] # Improved syntax for selection
    i1 = Concat(a, b) # Concatenation
    i2 = a + b # Improved syntax for concatenation
    j1 = Slice(1, 5, d) # Slicing of a bus
    j2 = d[1:5] # Improved syntax for slicing
    # /!\ As in the usual python syntax, the 5 is excluded
    # e.g. 1:5 means elements with index 1, 2, 3, 4
    # this is different than the netlist syntax, where the 5 would be included
    # Slice(1, 5, d) then corresponds to SLICE 1 4 d

    # RAM and ROM
    addr_size = 16
    word_size = 8
    read_addr = Input(addr_size)
    write_addr = Input(addr_size)
    write_enable = Input(1)
    write_data = Input(word_size)

    k1 = ROM(addr_size, word_size, read_addr)
    k2 = RAM(addr_size, word_size, read_addr, write_enable, write_addr, write_data)


# Expected output:
# INPUT a, b, c, d, read_addr, write_addr, write_enable, write_data
# OUTPUT g
# VAR a, b, c, d:8, read_addr:16, write_addr:16, write_enable, write_data:8, e1, e2, e3, e4, e5, e6, e7, e8:4, f1, f3, f4, f6, _l_16, g, h1, _d_sel_2, i1:2, i2:2, j1:4, _d_slc_1_4:4, k1:8, k2:8
# IN
# e1 = AND a b
# e2 = NAND a b
# e3 = OR a b
# e4 = XOR a b
# e5 = MUX c a b
# e6 = NOT a
# e7 = REG a
# e8 = 0010
# f1 = AND a b
# f3 = OR a b
# f4 = XOR a b
# f6 = NOT a
# _l_16 = OR a b
# g = AND _l_16 c
# h1 = SELECT 2 d
# _d_sel_2 = SELECT 2 d
# i1 = CONCAT a b
# i2 = CONCAT a b
# j1 = SLICE 1 4 d
# _d_slc_1_4 = SLICE 1 4 d
# k1 = ROM 16 8 read_addr
# k2 = RAM 16 8 read_addr write_enable write_addr write_data
