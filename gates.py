from abc import ABC, abstractmethod
from copy import deepcopy
import math
import random
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

        if isinstance(self, Const) and self.value != form.value:
            return None

        if len(self.children) != len(form.children):
            return None

        for i in range(len(self.children)):
            if self.children[i].match(form.children[i], variables) is None:
                return None

        return variables

    def substitute(self, variables):
        if isinstance(self, Var):
            if self.name not in variables:
                return None
            return variables[self.name]

        result = deepcopy(self)
        for i in range(len(result.children)):
            result.children[i] = result.children[i].substitute(variables)
            if result.children[i] is None:
                return None

        return result

    def neighbors(self):
        neighbors = []

        for rule in RULES:
            for variant in rule.variants:
                variables = self.match(variant.left, {})
                if variables is not None:
                    neighbor = variant.right.substitute(variables)
                    if neighbor is not None and neighbor not in neighbors:
                        neighbors.append(neighbor)

        for i in range(len(self.children)):
            for child_neighbor in self.children[i].neighbors():
                neighbor = deepcopy(self)
                neighbor.children[i] = child_neighbor
                if neighbor not in neighbors:
                    neighbors.append(neighbor)

        return neighbors

class Const(Node):
    def __init__(self, value):
        super().__init__([])
        self.value = value

    def __eq__(self, other):
        return super().__eq__(other) and other.value == self.value

    def __str__(self):
        return str(int(self.value))

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
    def __init__(self, left, right, include_inverse=False):
        self.left = left
        self.right = right
        self.variants = [ self ]
        if include_inverse:
            self.variants.append(Rule(right, left))

    def __str__(self):
        return f"{self.left} = {self.right}"

    def __repr__(self):
        return str(self)

RULES = [
    # Commutative properties
    # a + b = b + a
    # a * b = b * a
    Rule(Or(Var("a"), Var("b")), Or(Var("b"), Var("a")), True),
    Rule(And(Var("a"), Var("b")), And(Var("b"), Var("a")), True),

    # Associative properties
    # a + (b + c) = (a + b) + c
    # a * (b * c) = (a * b) * c
    Rule(Or(Var("a"), Or(Var("b"), Var("c"))), Or(Or(Var("a"), Var("b")), Var("c")), True),
    Rule(And(Var("a"), And(Var("b"), Var("c"))), And(And(Var("a"), Var("b")), Var("c")), True),

    # Distributive property
    # a * (b + c) = (a * b) + (a * c)
    Rule(And(Var("a"), Or(Var("b"), Var("c"))), Or(And(Var("a"), Var("b")), And(Var("a"), Var("c"))), True),

    # De Morgan's laws
    # !(a + b) = !a * !b
    # !(a * b) = !a + !b
    Rule(Not(Or(Var("a"), Var("b"))), And(Not(Var("a")), Not(Var("b"))), True),
    Rule(Not(And(Var("a"), Var("b"))), Or(Not(Var("a")), Not(Var("b"))), True),

    # a + a = a
    # a * a = a
    Rule(Or(Var("a"), Var("a")), Var("a")),
    Rule(And(Var("a"), Var("a")), Var("a")),

    # a + 0 = a
    # a + 1 = 1
    # a * 0 = 0
    # a * 1 = a
    Rule(Or(Var("a"), Const(False)), Var("a")),
    Rule(Or(Var("a"), Const(True)), Const(True)),
    Rule(And(Var("a"), Const(False)), Const(False)),
    Rule(And(Var("a"), Const(True)), Var("a")),

    # a + !a = 1
    # a * !a = 0
    Rule(Or(Var("a"), Not(Var("a"))), Const(True)),
    Rule(And(Var("a"), Not(Var("a"))), Const(False)),

    # a + (a * b) = a
    # a + (!a * b) = a + b
    # !a + (a * b) = !a + b
    Rule(Or(Var("a"), And(Var("a"), Var("b"))), Var("a")),
    Rule(Or(Var("a"), And(Not(Var("a")), Var("b"))), Or(Var("a"), Var("b"))),
    Rule(Or(Not(Var("a")), And(Var("a"), Var("b"))), Or(Not(Var("a")), Var("b"))),

    # !!a = a
    # !0 = 1
    # !1 = 0
    Rule(Not(Not(Var("a"))), Var("a")),
    Rule(Not(Const(False)), Const(True)),
    Rule(Not(Const(True)), Const(False))
]

def cost(expr):
    c = 1
    for child in expr.children:
        c += cost(child)
    return c

expr = Or(And(Var("a"), Var("b")), And(And(Var("b"), Var("c")), Or(Var("b"), Var("c"))))
iterations = 10000
for t in range(iterations):
    neighbors = expr.neighbors()
    neighbor = random.choice(neighbors)
    diff = cost(neighbor) - cost(expr)
    old = expr
    if diff < 0:
        expr = neighbor
    if random.random() < 0.01:
        expr = neighbor
    if expr != old:
        print(expr)
