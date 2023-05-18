from abc import ABC, abstractmethod
from copy import deepcopy
from pprint import pprint

class Node:
    def __init__(self, children):
        self.children = children

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return other.children == self.children

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return str(self)

    def match(self, form, variables):
        if isinstance(form, Var):
            if form.name in variables:
                if self != variables[form.name]:
                    return None
            else:
                variables[form.name] = self
                return variables

        if not isinstance(self, type(form)):
            return None

        if len(self.children) != len(form.children):
            return None

        for i in range(len(self.children)):
            if self.children[i].match(form.children[i], variables) is None:
                return None

        return variables

    def substitute(self, variables):
        result = deepcopy(self)
        for i in range(len(result.children)):
            if isinstance(result.children[i], Var):
                result.children[i] = variables[result.children[i].name]
            else:
                result.children[i] = result.children[i].substitute(variables)
        return result

    def neighbors(self):
        neighbors = []

        for rule in RULES:
            for variant in rule.variants:
                variables = self.match(variant.left, {})
                if variables is not None:
                    neighbor = variant.right.substitute(variables)
                    if neighbor not in neighbors:
                        neighbors.append(neighbor)

        for i in range(len(self.children)):
            for child_neighbor in self.children[i].neighbors():
                neighbor = deepcopy(self)
                neighbor.children[i] = child_neighbor
                if neighbor not in neighbors:
                    neighbors.append(neighbor)

        return neighbors

class Var(Node):
    def __init__(self, name):
        super().__init__([])
        self.name = name

    def __eq__(self, other):
        return super().__eq__(other) and other.name == self.name

    def __str__(self):
        return self.name

class Not(Node):
    def __init__(self, child):
        super().__init__([child])

    def __str__(self):
        return f"!{self.children[0]}"

class Binary(Node):
    def __init__(self, symbol, left, right):
        super().__init__([left, right])
        self.symbol = symbol

    def __str__(self):
        return f"({f' {self.symbol} '.join([str(child) for child in self.children])})"

class Or(Binary):
    def __init__(self, left, right):
        super().__init__("+", left, right)

class And(Binary):
    def __init__(self, left, right):
        super().__init__("*", left, right)

class Rule:
    def __init__(self, left, right, inverse=None):
        self.left = left
        self.right = right
        self.inverse = inverse or Rule(right, left, self)
        self.variants = [ self, self.inverse ]

    def __str__(self):
        return f"{self.left} = {self.right}"

    def __repr__(self):
        return str(self)

RULES = [
    # Commutative properties
    # a + b = b + a
    # a * b = b * a
    Rule(Or(Var("a"), Var("b")), Or(Var("b"), Var("a"))),
    Rule(And(Var("a"), Var("b")), And(Var("b"), Var("a"))),

    # Associative properties
    # a + (b + c) = (a + b) + c
    # a * (b * c) = (a * b) * c
    Rule(Or(Var("a"), Or(Var("b"), Var("c"))), Or(Or(Var("a"), Var("b")), Var("c"))),
    Rule(And(Var("a"), And(Var("b"), Var("c"))), And(And(Var("a"), Var("b")), Var("c"))),

    # Distributive property
    # a * (b + c) = (a * b) + (a * c)
    Rule(And(Var("a"), Or(Var("b"), Var("c"))), Or(And(Var("a"), Var("b")), And(Var("a"), Var("c")))),

    # De Morgan's laws
    # !(a + b) = !a * !b
    # !(a * b) = !a + !b
    Rule(Not(Or(Var("a"), Var("b"))), And(Not(Var("a")), Not(Var("b")))),
    Rule(Not(And(Var("a"), Var("b"))), Or(Not(Var("a")), Not(Var("b")))),

    # Simplification
    # a * a = a
    # a + a = a
    Rule(And(Var("a"), Var("a")), Var("a")),
    Rule(Or(Var("a"), Var("a")), Var("a")),
    # a * !a = False
    # a + !a = True
    Rule(And(Var("a"), Not(Var("a"))), False),
    Rule(Or(Var("a"), Not(Var("a"))), True)
]

expr = Or(And(Var("a"), Var("b")), And(And(Var("b"), Var("c")), Or(Var("b"), Var("c"))))
print(expr)
pprint(expr.neighbors())
