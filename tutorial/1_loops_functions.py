# SPDX-License-Identifier: CC0-1.0
# carotte.py by TWal, hbens & more

from lib_carotte import *

# In 0_basic.py, we saw how to write netlists using carotte.py.
# It looked like a normal netlist, but with weird syntax.
# Here, we will see how to use Python to generate netlists more easily

# If there is a circuit that you want to use at several places in the code, you can define it is a function like this:
def full_adder(a, b, c):
    tmp = a ^ b
    return (tmp ^ c, (tmp & c) | (a & b))

# You can do python loops to generate circuits
def n_adder(a, b):
    assert(a.bus_size == b.bus_size)
    c = Constant("0")
    (s, c) = full_adder(a[0], b[0], c) # Treat the 0 case separately since variables have a bus size >= 1
    for i in range(1, a.bus_size):
        (s_i, c) = full_adder(a[i], b[i], c)
        s = s + s_i
    return (s, c)

def main():
    a = Input(3)
    b = Input(3)
    (s, c) = n_adder(a, b)
    s.set_as_output("sum")
    c.set_as_output("overflow")

# Expected output:
# INPUT a, b
# OUTPUT sum, overflow
# VAR a:3, b:3, c, _a_sel_0, _b_sel_0, tmp, s, _l_7, _l_8, _c_10, _a_sel_1, _b_sel_1, _tmp_14, s_i, _l_16, _l_17, _c_19, _s_21:2, _a_sel_2, _b_sel_2, _tmp_25, _s_i_30, _l_27, _l_28, overflow, sum:3
# IN
# c = 0
# _a_sel_0 = SELECT 0 a
# _b_sel_0 = SELECT 0 b
# tmp = XOR _a_sel_0 _b_sel_0
# s = XOR tmp c
# _l_7 = AND tmp c
# _l_8 = AND _a_sel_0 _b_sel_0
# _c_10 = OR _l_7 _l_8
# _a_sel_1 = SELECT 1 a
# _b_sel_1 = SELECT 1 b
# _tmp_14 = XOR _a_sel_1 _b_sel_1
# s_i = XOR _tmp_14 _c_10
# _l_16 = AND _tmp_14 _c_10
# _l_17 = AND _a_sel_1 _b_sel_1
# _c_19 = OR _l_16 _l_17
# _s_21 = CONCAT s s_i
# _a_sel_2 = SELECT 2 a
# _b_sel_2 = SELECT 2 b
# _tmp_25 = XOR _a_sel_2 _b_sel_2
# _s_i_30 = XOR _tmp_25 _c_19
# _l_27 = AND _tmp_25 _c_19
# _l_28 = AND _a_sel_2 _b_sel_2
# overflow = OR _l_27 _l_28
# sum = CONCAT _s_21 _s_i_30
