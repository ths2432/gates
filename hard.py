from abc import ABC, abstractmethod
from copy import deepcopy
from pprint import pprint

class Term(ABC):
    def __init__(self, children):
        self.children = children

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.children == self.children

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return str(self)

    @abstractmethod
    def eval(self, variables):
        pass

    def inputs(self):
        inputs = set()
        for child in self.children:
            inputs = inputs | child.inputs()
        return inputs

    def equivalent(self, other):
        def permute(n):
            array = []
            permutations = 2 ** n - 1
            while (permutations >= 0):
                binary = str(bin(permutations))[2:]
                while (len(binary) < n):
                    binary = "0" + binary
                array.append([bool(int(a)) for a in binary])
                permutations = permutations - 1
            return array

        inputs = list(self.inputs() | other.inputs())
        permutations = permute(len(inputs))
        for permutation in permutations:
            variables = {}
            for i in range(len(inputs)):
                variables[inputs[i].name] = permutation[i]
            if self.eval(variables) != other.eval(variables):
                return False
        return True

    def match(self, redex, variables):
        if not isinstance(redex, type(self)):
            return False
        for i in range(len(self.children)):
            if not self.children[i].match(redex.children[i], variables):
                return False
        return True

    def substitute(self, variables):
        result = deepcopy(self)
        for i in range(len(result.children)):
            result.children[i] = result.children[i].substitute(variables)
        return result

    def neighbors(self):
        neighbors = set()

        for rule in RULES:
            variables = {}
            if rule[0].match(self, variables):
                neighbor = rule[1].substitute(variables)
                if neighbor is not None and neighbor not in neighbors:
                    neighbors.add(neighbor)

        for i in range(len(self.children)):
            for child_neighbor in self.children[i].neighbors():
                neighbor = deepcopy(self)
                neighbor.children[i] = child_neighbor
                if neighbor not in neighbors:
                    neighbors.add(neighbor)

        return neighbors

    def cost(self):
        # TODO : Return the integer number of terms of the full expression
        raise NotImplementedError

    def simplify(self):
        # TODO : Return the most simplified logical expression using all the RULES
        raise NotImplementedError


class Constant(Term):
    def __init__(self, value):
        super().__init__([])
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Constant) and other.value == self.value

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return str(int(self.value))

    def eval(self, variables):
        # TODO : Return its value
        raise NotImplementedError

    def match(self, redex, variables):
        return redex == self


class Variable(Term):
    def __init__(self, name):
        super().__init__([])
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Variable) and other.name == self.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def eval(self, variables):
        # TODO : Return its value using its name (self.name) and the variables dictionary
        raise NotImplementedError

    def inputs(self):
        return {self}

    def match(self, redex, variables):
        if self.name in variables:
            if redex != variables[self.name]:
                return False
            else:
                return True
        else:
            variables[self.name] = redex
            return True

    def substitute(self, variables):
        return variables[self.name]


class Not(Term):
    def __init__(self, child):
        super().__init__([child])

    def __hash__(self):
        return hash(self.children[0])

    def __str__(self):
        return f"!{self.children[0]}"

    def eval(self, variables):
        return not self.children[0].eval(variables)


class Binary(Term):
    def __init__(self, left, right, symbol):
        super().__init__([left, right])
        self.symbol = symbol

    def __hash__(self):
        return hash((self.children[0], self.children[1]))

    def __str__(self):
        return f"({self.children[0]} {self.symbol} {self.children[1]})"


class Or(Binary):
    def __init__(self, left, right):
        super().__init__(left, right, "+")

    def eval(self, variables):
        # TODO : Return the correct value for an OR gate
        raise NotImplementedError


class And(Binary):
    def __init__(self, left, right):
        super().__init__(left, right, "*")

    def eval(self, variables):
        # TODO : Return the correct value for an AND gate
        raise NotImplementedError


RULES = {

    # Associative properties (and their inverses)
    # a + (b + c) = (a + b) + c
    # a * (b * c) = (a * b) * c
    (Or(Variable("a"), Or(Variable("b"), Variable("c"))),
     Or(Or(Variable("a"), Variable("b")), Variable("c"))),
    (Or(Or(Variable("a"), Variable("b")), Variable("c")),
     Or(Variable("a"), Or(Variable("b"), Variable("c")))),
    (And(Variable("a"), And(Variable("b"), Variable("c"))),
     And(And(Variable("a"), Variable("b")), Variable("c"))),
    (And(And(Variable("a"), Variable("b")), Variable("c")),
     And(Variable("a"), And(Variable("b"), Variable("c")))),

    # Distributive property
    # a * (b + c) = (a * b) + (a * c)
    (And(Variable("a"), Or(Variable("b"), Variable("c"))),
     Or(And(Variable("a"), Variable("b")), And(Variable("a"), Variable("c")))),
    (Or(And(Variable("a"), Variable("b")), And(Variable("a"), Variable("c"))),
     And(Variable("a"), Or(Variable("b"), Variable("c")))),

    # TODO: De Morgan's Laws
    # !(a + b) = !a * !b
    # !(a * b) = !a + !b

    # TODO: Commutative Properties
    # a + b = b + a
    # a * b = b * a

    # TODO: Single Variable Theorems
    # a + a = a
    # a * a = a

    # a + 0 = a
    # a + 1 = 1
    # a * 0 = 0
    # a * 1 = a

    # a + !a = 1
    # a * !a = 0

    # !!a = a
    # !0 = 1
    # !1 = 0

    # TODO: Double Variable Theorems
    # a + (a * b) = a
    # a + (!a * b) = a + b
    # !a + (a * b) = !a + b
    }