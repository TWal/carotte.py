# SPDX-License-Identifier: CC0-1.0
# carotte.py by Twal, hbens & more

'''Carotte library internals'''

import sys
import typing


class FakeColorama:
    '''We define here empty variables for when the colorama package is not available'''
    def __init__(self, depth: int = 0):
        if depth < 1:
            self.Fore = FakeColorama(depth+1)
            self.Fore.YELLOW = '' # type: ignore
            self.Style = FakeColorama(depth+1)
            self.Style.RESET_ALL = '' # type: ignore

try:
    import colorama  # type: ignore
except ModuleNotFoundError:
    print("Warning: Install module 'colorama' for colored errors", file=sys.stderr)
    colorama = FakeColorama() # type: ignore

_equation_counter = 0
_input_list: typing.List['Variable'] = []
_equation_list: typing.List['Variable'] = []
_output_list = []
_name_set = set()
_unevaluated_defer_set = set()
_ALLOW_RIBBON_LOGIC_OPERATIONS = False

def allow_ribbon_logic_operations(enable : bool) -> None:
    '''Enable or disable ribbon logic operations'''
    global _ALLOW_RIBBON_LOGIC_OPERATIONS # pylint: disable=W0603
    _ALLOW_RIBBON_LOGIC_OPERATIONS = enable

def get_and_increment_equation_counter() -> int:
    '''Return the current global equation counter, and increment it'''
    global _equation_counter # pylint: disable=W0603
    old_value = _equation_counter
    _equation_counter += 1
    return old_value

class Variable(typing.Sequence['Variable']):
    '''The basis of carotte.py: netlist variables core'''
    def __init__(self, name: str, bus_size: int, autogen_name: bool = True):
        assert name not in _name_set
        assert bus_size >= 0
        _name_set.add(name)
        self.name = name
        self.autogen_name = autogen_name
        self.bus_size = bus_size
    def set_as_output(self, name: typing.Optional[str] = None) -> None:
        '''Sets this variable as a netlist OUTPUT'''
        if name is not None:
            self.rename(name)
        _output_list.append(self)
    def get_full_name(self) -> str:
        '''Returns the full name of this variable for the VARIABLE part of the netlist'''
        if self.bus_size == 1:
            return self.name
        return f"{self.name}:{self.bus_size}"

    def rename(self, new_name: str, autogen_name: bool = False) -> None:
        '''Rename the variable; can fail'''
        if self.name != new_name:
            if new_name in _name_set:
                raise ValueError(f"Rename failed: the variable name '{new_name}' is already used!")
            _name_set.remove(self.name)
            _name_set.add(new_name)
            self.name = new_name
            self.autogen_name = autogen_name

    def try_rename(self, new_name: str, autogen_name: bool = False) -> bool:
        '''Rename the variable if the new name is available and deemed better than the old one'''
        if not self.autogen_name and autogen_name:
            return False
        try:
            self.rename(new_name, autogen_name)
        except ValueError:
            return False
        return True

    def __assignpre__(self, lhs_name: str, rhs_name: str, rhs: typing.Any) -> typing.Any:
        '''Magic hook for better variables names'''
        if False: # pylint: disable=W0125
            print(f'{colorama.Fore.YELLOW}PRE: assigning {lhs_name} = {rhs_name}  ||| var: {rhs.get_full_name()}')
        return rhs

    def __assignpost__(self, lhs_name: str, rhs_name: str) -> None:
        '''Magic hook for better variables names'''
        if False: # pylint: disable=W0125
            print(f'POST: assigning {lhs_name} = {rhs_name}  ||| var{self.autogen_name}: {self.get_full_name()}')
        if self.autogen_name and (lhs_name is not None):
            new_name = lhs_name
            if new_name in _name_set:
                new_name = '_' + lhs_name + '_' + str(get_and_increment_equation_counter())
            self.try_rename(new_name)

    def __and__(self, rhs: 'Variable') -> 'Variable':
        return And(self, rhs)
    def __or__(self, rhs: 'Variable') -> 'Variable':
        return Or(self, rhs)
    def __xor__(self, rhs: 'Variable') -> 'Variable':
        return Xor(self, rhs)
    def __invert__(self) -> 'Variable':
        return Not(self)
    def __len__(self) -> int:
        return self.bus_size
    def __getitem__(self, index: typing.Union[int, slice]) -> 'Variable':
        if isinstance(index, slice):
            if (index.step is not None) and (index.step != 1):
                raise TypeError(f"Slices must use a step of '1' (have {index.step})")
            start = 0 if index.start is None else index.start
            stop = self.bus_size if index.stop is None else index.stop
            return Slice(start, stop, self)
        if isinstance(index, int):
            return Select(index, self)
        raise TypeError(f"Invalid getitem, index: {index} is neither a slice or an integer")
    def __add__(self, rhs: 'Variable') -> 'Variable':
        return Concat(self, rhs)

class Defer:
    '''For handling loops in variable declarations'''
    def __init__(self, bus_size: int, lazy_val: typing.Callable[[], Variable]):
        self.val: typing.Optional[Variable] = None
        self.lazy_val = lazy_val
        self.bus_size = bus_size
        _unevaluated_defer_set.add(self)
    def get_val(self) -> Variable:
        '''Helper to resolve the variable value once the loop issue has been solved'''
        if self.val is None:
            _unevaluated_defer_set.remove(self)
            self.val = self.lazy_val()
            assert self.val.bus_size == self.bus_size
        return self.val
    def __getattr__(self, attr: str) -> str:
        if attr == 'name':
            return self.get_val().name
        if attr == 'bus_size':
            return self.bus_size
        if attr == 'autogen_name':
            return True
        raise AttributeError

VariableOrDefer = typing.Union[Variable, Defer]

class Input(Variable):
    '''A netlist variable of type INPUT'''
    def __init__(self, bus_size: int, name: typing.Optional[str] = None):
        autogen_name = False
        if name is None:
            name = "_input_" + str(get_and_increment_equation_counter())
            autogen_name = True
        if name in _name_set:
            raise ValueError(f"The variable name '{name}' is already used!")
        super().__init__(name, bus_size, autogen_name)
        _input_list.append(self)
    def __str__(self) -> str:
        return self.name

class EquationVariable(Variable):
    '''A standard netlist variable'''
    def __init__(self, bus_size: int):
        while True:
            name = "_l_" + str(get_and_increment_equation_counter())
            if name not in _name_set:
                break
        super().__init__(name, bus_size)
        _equation_list.append(self)

class Constant(EquationVariable):
    '''Netlist constant'''
    def __init__(self, value: str):
        if len(value) == 0:
            raise ValueError("Defining an empty constant is not allowed")
        for x in value:
            if x not in "01tf":
                raise ValueError(f"The character {x} of the constant {value} is not allowed"
                    + " (it should either be 0, 1, t or f)")
        super().__init__(len(value))
        self.value = value
    def __str__(self) -> str:
        return f"{self.name} = {self.value}"

class Unop(EquationVariable):
    '''Netlist unary operations on variables'''
    unop_name = ""
    def __init__(self, x: VariableOrDefer):
        if not _ALLOW_RIBBON_LOGIC_OPERATIONS and x.bus_size != 1:
            raise ValueError(f"Unops can only be performed on signals of bus size 1 (have {x.bus_size}). "
                             + "If your simulator handles ribbons logic operations, "
                             + "call `allow_ribbon_logic_operations(True)`")
        super().__init__(x.bus_size)
        self.x = x
    def __str__(self) -> str:
        if self.unop_name == "":
            raise ValueError("MEH")
        return f"{self.name} = {self.unop_name} {self.x.name}"

class Not(Unop):
    '''Netlist NOT'''
    unop_name = "NOT"

class Reg(Unop):
    '''Netlist REG'''
    unop_name = "REG"

class Binop(EquationVariable):
    '''Netlist binary operations on variables'''
    binop_name = ""
    def __init__(self, lhs: VariableOrDefer, rhsB: VariableOrDefer):
        if lhs.bus_size != rhsB.bus_size:
            raise ValueError(f"Operands have different bus sizes: {lhs.bus_size} and {rhsB.bus_size}")
        if not _ALLOW_RIBBON_LOGIC_OPERATIONS and lhs.bus_size != 1:
            raise ValueError(f"Binops can only be performed on signals of bus size 1 (have {lhs.bus_size}). "
                             + "If your simulator handles ribbons logic operations, "
                             + "call `allow_ribbon_logic_operations(True)`")
        super().__init__(lhs.bus_size)
        self.lhs = lhs
        self.rhs = rhsB
    def __str__(self) -> str:
        if self.binop_name == "":
            raise ValueError("MEH")
        return f"{self.name} = {self.binop_name} {self.lhs.name} {self.rhs.name}"

class And(Binop):
    '''Netlist AND'''
    binop_name = "AND"
class Nand(Binop):
    '''Netlist NAND'''
    binop_name = "NAND"
class Or(Binop):
    '''Netlist OR'''
    binop_name = "OR"
class Xor(Binop):
    '''Netlist XOR'''
    binop_name = "XOR"

class Mux(EquationVariable):
    '''Netlist MUX'''
    def __init__(self, choice: VariableOrDefer, a: VariableOrDefer, b: VariableOrDefer):
        if choice.bus_size != 1:
            raise ValueError(f"MUX choice bus size must be 1, have {choice.bus_size}")
        if a.bus_size != b.bus_size:
            raise ValueError(f"MUX sides must have the same bus size, have {a.bus_size} and {b.bus_size}")
        self.choice = choice
        self.a = a
        self.b = b
        super().__init__(a.bus_size)
    def __str__(self) -> str:
        return f"{self.name} = MUX {self.choice.name} {self.a.name} {self.b.name}"

class ROM(EquationVariable):
    '''Netlist ROM'''
    def __init__(self, addr_size: int, word_size: int, read_addr: VariableOrDefer):
        if read_addr.bus_size != addr_size:
            raise ValueError(f"ROM read address bus size ({read_addr.bus_size}) must be equal "
                + "to addr_size ({addr_size})")
        self.addr_size = addr_size
        self.word_size = word_size
        self.read_addr = read_addr
        super().__init__(word_size)
    def __str__(self) -> str:
        return f"{self.name} = ROM {self.addr_size} {self.word_size} {self.read_addr.name}"

class RAM(EquationVariable):
    '''Netlist RAM'''
    def __init__(self, addr_size: int, word_size: int, read_addr: VariableOrDefer,
                 write_enable: VariableOrDefer, write_addr: VariableOrDefer, write_data: VariableOrDefer):
        if read_addr.bus_size != addr_size:
            raise ValueError(f"RAM read address bus size ({read_addr.bus_size}) must be equal "
                + "to addr_size ({addr_size})")
        if write_enable.bus_size != 1:
            raise ValueError(f"RAM write_enable bus size must be equal to 1, have {write_enable.bus_size}")
        if write_addr.bus_size != addr_size:
            raise ValueError(f"RAM write address bus size ({write_addr.bus_size}) must be equal "
                + "to addr_size ({addr_size})")
        if write_data.bus_size != word_size:
            raise ValueError(f"RAM write data bus size ({write_data.bus_size}) must be equal "
                + "to word_size ({word_size})")
        self.addr_size = addr_size
        self.word_size = word_size
        self.read_addr = read_addr
        self.write_enable = write_enable
        self.write_addr = write_addr
        self.write_data = write_data
        super().__init__(word_size)
    def __str__(self) -> str:
        return (f"{self.name} = RAM {self.addr_size} {self.word_size} {self.read_addr.name} " +
                f"{self.write_enable.name} {self.write_addr.name} {self.write_data.name}")

class Concat(EquationVariable):
    '''Netlist CONCAT'''
    def __init__(self, lhs: VariableOrDefer, rhs: VariableOrDefer):
        super().__init__(lhs.bus_size + rhs.bus_size)
        self.lhs = lhs
        self.rhs = rhs
    def __str__(self) -> str:
        return f"{self.name} = CONCAT {self.lhs.name} {self.rhs.name}"

class Slice(EquationVariable):
    '''Netlist SLICE'''
    def __init__(self, i1: int, i2: int, x: VariableOrDefer):
        if not 0 <= i1 < i2 <= x.bus_size:
            raise IndexError(f"Slice must satisfy `0 <= i1 < i2 <= bus_size`, i.e. {0} <= {i1} < {i2} <= {x.bus_size}")
        super().__init__(i2-i1)
        self.i1 = i1
        self.i2 = i2-1
        self.x = x
        if not x.autogen_name and '_slc_' not in x.name:
            self.try_rename(('' if x.name.startswith('_') else '_') + x.name + '_slc_' +
                            str(self.i1) + '_' + str(self.i2), True)
    def __str__(self) -> str:
        return f"{self.name} = SLICE {self.i1} {self.i2} {self.x.name}"

class Select(EquationVariable):
    '''Netlist SELECT'''
    def __init__(self, i: int, x: VariableOrDefer):
        if not 0 <= i < x.bus_size:
            raise IndexError(f"Select must satisfy `0 <= i < bus_size`, i.e. {0} <= {i} < {x.bus_size}")
        super().__init__(1)
        self.i = i
        self.x = x
        if not x.autogen_name:
            self.try_rename(('' if x.name.startswith('_') else '_') + x.name + '_sel_' + str(i), True)
    def __str__(self) -> str:
        return f"{self.name} = SELECT {self.i} {self.x.name}"

def get_netlist() -> str:
    '''Get the netlist in string form'''

    # The equations might contain Defer nodes that are not yet evaluated,
    # and their evaluation could create new equations.
    # This loop evaluates all Defer nodes (and subsequent Defer nodes that could
    # be created by the evaluation of the previous ones)
    while len(_unevaluated_defer_set) != 0:
        for defer in list(_unevaluated_defer_set):
            defer.get_val()

    old_lens = (len(_input_list), len(_output_list), len(_equation_list))

    netlist = (
        ""
        + "INPUT " + ", ".join(x.name for x in _input_list) + "\n"
        + "OUTPUT " + ", ".join(x.name for x in _output_list) + "\n"
        + "VAR " + ", ".join(x.get_full_name() for x in _input_list + _equation_list) + "\n"
        + "IN" + "\n"
        + "".join(str(x) + "\n" for x in _equation_list)
    )

    # Sanity check
    new_lens = (len(_input_list), len(_output_list), len(_equation_list))
    if new_lens != old_lens:
        raise RuntimeError("Internal error: inconsistent lengths, please report a bug")

    return netlist

def reset() -> None:
    '''Reset the netlist'''
    global _equation_counter, _input_list, _equation_list, _output_list, _name_set # pylint: disable=W0603
    _equation_counter = 0
    _input_list = []
    _equation_list = []
    _output_list = []
    _name_set = set()
