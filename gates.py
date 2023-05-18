from abc import ABC, abstractmethod
import copy
import random

# TODO:
# - Implement the not gate
# - Add the rest of the rules
# - Simulated annealing maybe?

class Node(ABC):
    def __init__(self, children):
        self.children = children
        pass

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return self.children == other.children

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return str(self)

    def matches(self, expr, vars={}):
        if type(expr) == Var:
            if expr.name in vars:
                if self != vars[expr.name]:
                    return False
            else:
                vars[expr.name] = self
                return True

        if not isinstance(self, type(expr)):
            return False

        if not len(self.children) == len(expr.children):
            return False
        
        for i in range(len(self.children)):
            if not self.children[i].matches(expr.children[i], vars):
                return False

        return True

    def substitute(self, vars):
        result = copy.deepcopy(self)
        for i in range(len(result.children)):
            if isinstance(result.children[i], Var):
                result.children[i] = vars[result.children[i].name]
            else:
                result.children[i] = result.children[i].substitute(vars)
        return result

    def neighbors(self, rules):
        neighbors = []

        if hasattr(self, "children"):
            for i in range(len(self.children)):
                for neighbor in self.children[i].neighbors(rules):
                    full = copy.deepcopy(self)
                    full.children[i] = neighbor
                    neighbors.append(full)

        for rule in rules:
            vars = {}
            if self.matches(rule.left, vars):
                neighbors.append(rule.right.substitute(vars))
            
        return neighbors

    def complexity(self):
        complexity = 1
        if hasattr(self, "children"):
            for child in self.children:
                complexity += child.complexity()
        return complexity

    def simplify(self, rules):
        state = self
        while True:
            print(state)
            neighbors = self.neighbors(rules)
            state = random.choice(neighbors)


class Var(Node):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, Var):
            return False

        return self.name == other.name

    def __str__(self):
        return self.name

class Or(Node):
    def __init__(self, left, right):
        super().__init__([left, right])

    def __str__(self):
        return f"({self.children[0]} + {self.children[1]})"

class And(Node):
    def __init__(self, left, right):
        super().__init__([left, right])

    def __str__(self):
        return f"({self.children[0]} * {self.children[1]})"

class Rule:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return str([self.left, self.right])

rules = [
    # Commutative laws
    Rule(
        Or(Var("a"), Var("b")),
        Or(Var("b"), Var("a"))
    ),
    Rule(
        And(Var("a"), Var("b")),
        And(Var("b"), Var("a"))
    ),
    # Associative laws
    Rule(
        Or(Var("a"), Or(Var("b"), Var("c"))),
        Or(Or(Var("a"), Var("b")), Var("c")),
    ),
    Rule(
        And(Var("a"), And(Var("b"), Var("c"))),
        And(And(Var("a"), Var("b")), Var("c")),
    ),
    # Distributive law
    Rule(
        And(Var("a"), Or(Var("b"), Var("c"))),
        Or(And(Var("a"), Var("b")), And(Var("a"), Var("c"))),
    ),
    # Simplification theorems
    Rule(
        Or(Var("a"), Var("a")),
        Var("a")
    ),
    Rule(
        And(Var("a"), Var("a")),
        Var("a")
    ),
    Rule(
        Or(Var("a"), And(Var("a"), Var("b"))),
        Var("a")
    )
]

expr = Or(And(Var("a"), Var("b")), And(And(Var("b"), Var("c")), Or(Var("b"), Var("c"))))
print(expr.simplify(rules))
