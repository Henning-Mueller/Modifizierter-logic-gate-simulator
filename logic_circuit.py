"""
Logic Circuits

This module allows you to define logic gates and join them together into a logic
circuit. Cricuit components output either True, False or None. By default all
components ouput None by default.

This module depends on boolean.py, which can be found at: 
https://github.com/qqii/boolean.py
"""
import itertools

import boolean


class Component:

    """
    Base class for all cricuit components
    """

    def __init__(self):
        self.inputs = {}

    def __contains__(self, comp):
        if comp in self.inputs.values():
            return True
        elif comp in self.inputs.keys():
            return True
        return False

    def __repr__(self):
        return "<{name}({inputs}, {expr}, {output})>".format(
            name=self.__class__.__name__,
            inputs=repr(self.inputs),
            expr=repr(self.expression),
            output=repr(self.output))

    @property
    def output(self):
        return None

    @property
    def expression(self):
        return None

    @property
    def empty_input_keys(self):
        return tuple(k for k, v in self.inputs.items() if v is None)

    def update(self):
        """
        Recalculates the component's output.
        """
        pass

    def remove(self, board):
        """
        Removes itself from other components in the board that contains it.

        This does not change the output of the components.
        """
        for c in board.copy():
            while self in c:
                index = tuple(c.inputs.values()).index(self)
                key = tuple(c.inputs.keys())[index]
                c.inputs[key] = None
        # fixes possible memory leak
        self.inputs = {k: None for k, v in self.inputs.items()}


class Gate(Component):

    """
    Base class for all logic gates.

    Logic gates contain expressions which are evaluated on inputs. 
    """

    def __init__(self,
                 expression=None,
                 input_dict={},
                 anonymous_symbols=True):
        Component.__init__(self)
        self._output = None

        if isinstance(expression, str):
            expression = boolean.parse(expression)
        if not isinstance(expression, boolean.Expression):
            raise ValueError("Argument must be of type str or Expression but is type {}"
                             .format(expression.__class__))

        if anonymous_symbols:
            new_input_dict = {}
            for symbol in (s for s in expression.symbols.copy()):
                           # if s.obj != None):
                new_symbol = boolean.Symbol(None)
                expression = expression.subs({symbol: new_symbol})
                if input_dict.get(symbol) is not None:
                    new_input_dict[new_symbol] = input_dict[symbol]
                elif input_dict.get(str(symbol)) is not None:
                    new_input_dict[new_symbol] = input_dict[str(symbol)]
            input_dict = new_input_dict
        else:
            def symbol_if_string(e):
                if isinstance(e, str):
                    return boolean.Symbol(e)
                elif isinstance(e, boolean.Symbol):
                    return e
                else:
                    raise TypeError("Argument must be of type str of Symbol but is type {}"
                                    .format(e.__class__))
            input_dict = {symbol_if_string(k): v
                          for k, v in input_dict.items()}

        self._expression = expression
        # inputs maps symbols to components
        # This can make an output to itself
        self.inputs = {s: None for s in expression.symbols}
        self.inputs.update(input_dict)

    @property
    def output(self):
        return self._output

    @property
    def expression(self):
        return self._expression

    def update(self):
        inputs = self.inputs

        # If not any values in the dictionary are None
        if not any(True for v in inputs.values()
                   if v is None or v.output is None):
            subs_dict = {k: v.output for k, v in inputs.items()
                         if k in self.expression.symbols}
            self._output = bool(self.expression.subs(subs_dict))
        else:
            self._output = None


# The following classes are just for ease of programming
class And(Gate):

    def __init__(self,
                 inputs=(None, None),
                 anonymous_symbols=True):
        Gate.__init__(self,
                      expression="A*B",
                      input_dict={"A": inputs[0], "B": inputs[1]},
                      anonymous_symbols=anonymous_symbols)


class Or(Gate):

    def __init__(self,
                 inputs=(None, None),
                 anonymous_symbols=True):
        Gate.__init__(self,
                      expression="A+B",
                      input_dict={"A": inputs[0], "B": inputs[1]},
                      anonymous_symbols=anonymous_symbols)


class Not(Gate):

    def __init__(self,
                 input=None,
                 anonymous_symbols=True):
        Gate.__init__(self,
                      expression="~A",
                      input_dict={"A": input},
                      anonymous_symbols=anonymous_symbols)


class Nand(Gate):

    def __init__(self,
                 inputs=(None, None),
                 anonymous_symbols=True):
        Gate.__init__(self,
                      expression="~(A*B)",
                      input_dict={"A": inputs[0], "B": inputs[1]},
                      anonymous_symbols=anonymous_symbols)


class Nor(Gate):

    def __init__(self,
                 inputs=(None, None),
                 anonymous_symbols=True):
        Gate.__init__(self,
                      expression="~(A+B)",
                      input_dict={"A": inputs[0], "B": inputs[1]},
                      anonymous_symbols=anonymous_symbols)


# A wire is just a repeater gate
# Each wire contributes to the propagation delay
class Wire(Gate):

    """
    A wire.

    Wires can be used to connect outputs to inputs.
    """

    def __init__(self,
                 input=None,
                 symbol=None,
                 anonymous_symbols=True):
        if isinstance(symbol, (str, type(None))):
            symbol = boolean.Symbol(symbol)
        if not isinstance(symbol, boolean.Symbol):
            raise ValueError("Argument must be of type str or Symbol but is type {}"
                             .format(symbol.__class__))

        Gate.__init__(self,
                      expression=symbol,
                      input_dict={symbol: input},
                      anonymous_symbols=anonymous_symbols)

    @property
    def input(self):
        return self.inputs[self.expression]

    @input.setter
    def input(self, input):
        if isinstance(input, Output):
            raise TypeError("Output cannot be set as an input")
        self.inputs[self.expression] = input


class Input(Component):

    """
    An input.

    Inputs are used to input values into circuits.
    """

    def __init__(self,
                 output=False):
        self.output = output

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, output):
        self._output = bool(output)

    @property
    def expression(self):
        return None

    @property
    def inputs(self):
        return {}

    @property
    def emtpy_input_keys(self):
        return ()

    def update(self):
        pass

    def remove(self, board):
        # inputs = {} for all Inputs
        for c in board.copy():
            if self in c:
                index = tuple(c.inputs.values()).index(self)
                key = tuple(c.inputs.keys())[index]
                c.inputs[key] = None


class Switch(Input):

    def press(self):
        """
        Toggles output.
        """
        self.output = not self.output

    def click(self):
        """
        Toggles output.
        """
        self.press()


# The only difference between Wire and Output is that you should not link Output
# to an input
class Output(Wire):

    """
    An output.

    Output are used to display the output from a component.

    The output of an input should not be connected to something.
    """
    pass


class Bulb(Output):
    pass


class CircuitBoard(list):

    """
    A collection of components.

    Components in a circuit board do not all have to be connected together.
    Circuit boards can be updated by calling update. This allows the signals to
    propagate by 1 more component.

    Splices of circuit boards should only be read from and not updated.
    """

    def __init__(self,
                 component_list=[]):
        super().__init__(component_list)

    def update(self):
        """
        Updates all components.

        Components are updated in the following order:
            Inputs
            Wires
            Gates
            Other Components
            Outputs
        """
        def sort_key(component):
            if isinstance(component, Input):
                return 0
            if isinstance(component, Wire):
                return 1
            if isinstance(component, Gate):
                return 2
            if isinstance(component, Output):
                return 4
            return 3
        for c in sorted(self, key=sort_key):
            c.update()

    def remove(self, value):
        super().remove(value)
        value.remove(self)


# TODO: Make this accept the component in question
class RecursionError(Exception):

    """
    This is thrown instated of a StackOverflow.
    """
    pass


def expression(component, anonymous_symbols=False):
    """
    Takes a component and converts it into an expression.

    This function raises RecursionError if any component is self referencing.
    """
    # <x> in set() is faster than list
    seen = set()
    # An input can output into multiple components
    # This maps inputs -> symbols
    component_dict = {}

    def recursive_expression(c):
        """
        Recursively creates an expression from a component.

        his function raises RecursionError if any component is self referencing.
        """
        if c in (None, True, False):
            # The component is not connected to anything
            # Act as if they are connected to an input
            return boolean.Symbol(None)
        elif c in seen:
            raise RecursionError(
                "The logic circuit is self referencing and cannot be converted into a boolean expression")

        if not isinstance(c, Input):
            # Inputs can appear twice in the circuit
            seen.add(c)

        if isinstance(c, Input):
            if c in component_dict.keys():
                return component_dict[c]
            else:
                component_dict[c] = boolean.Symbol(None)
                return component_dict[c]
        elif isinstance(c, (Output, Wire)):
            # Wires don't matter
            return recursive_expression(c.input)
        elif isinstance(c, Gate):
            subs_dict = {}
            for k, v in c.inputs.items():
                subs_dict[k] = recursive_expression(v)
            return c.expression.subs(subs_dict, eval=False)

    if anonymous_symbols:
        return recursive_expression(component)
    else:
        def letters_generator():
            """
            Returns a generator that outputs A^n->Z^n for n->inf.
            Where <letter>^n = <letter><letter>^(n-1)
            """
            def multiletters(seq):
                for n in itertools.count(1):
                    for s in itertools.product(seq, repeat=n):
                        yield "".join(s)
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            return multiletters(letters)

        expression = recursive_expression(component)
        subs_dict = {}
        g = letters_generator()
        for s in expression.symbols:
            subs_dict[s] = boolean.Symbol(g.__next__())

        return expression.subs(subs_dict, eval=False)


def circuit_board(expression, bulb=True, eval=False):
    """
    Takes an expression and converts it into a circuit board.
    """
    if isinstance(expression, str):
        expression = boolean.parse(expression, eval=eval)
    if not isinstance(expression, boolean.Expression):
        raise TypeError(
            "Argument must be str or Expression but it is {}"
            .format(expression.__class__))

    # A list would work equally as well
    b = CircuitBoard()
    # A symbol can exist multiple times in an expression
    symbol_dict = {}

    def recursive_gate(e):
        """
        Recursively adds components to the circuit board.
        """
        if isinstance(e, boolean.BaseElement):
            # TODO: Either make the the same or create a constant component.
            s = Switch()
            b.append(s)
            return s
        elif isinstance(e, boolean.Symbol):
            if e in symbol_dict.keys():
                return symbol_dict[e]
            else:
                s = Switch()
                symbol_dict[e] = s
                b.append(s)
                return s
        elif isinstance(e, boolean.Function):
            # All gates are of type Gate instead of And, Or and Not
            if e.order == (1, 1):
                pre = recursive_gate(e.args[0])
                w = Wire(pre)
                b.append(w)

                s = boolean.Symbol(None)
                g = Gate(e.subs({e.args[0]: s}),
                         {s: w})
                b.append(g)
                return g
            else:
                input_dict = {}
                expr = e
                for arg in e.args:
                    pre = recursive_gate(arg)
                    w = Wire(pre)
                    b.append(w)

                    s = boolean.Symbol(None)
                    expr = expr.subs({arg: s})
                    input_dict[s] = w
                g = Gate(expr,
                         input_dict)
                b.append(g)
                return g
    recursive_gate(expression)
    if bulb:
        # Due to the nature of recursive_gate, the last component is last in the list
        w = Wire(b[-1])
        o = Bulb(w)
        b.append(w)
        b.append(o)
    return b
