from lib_carotte import *

def main() -> None:
    reg0 = Reg(Defer(1, lambda : Reg(Defer(1, lambda: c[0]))))
    c = reg0
