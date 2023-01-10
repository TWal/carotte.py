from lib_carotte import *

def main() -> None:
    reg0 = Reg(Select(0, Defer(1, lambda: c)))
    c = reg0
