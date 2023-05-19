from abc import ABC, abstractmethod
from copy import deepcopy

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

    def match(self, redex, variables):
        if not isinstance(redex, type(self)):
            return False
        for i in range(len(self.children)):
            if not self.children[i].match(redex.children[i], variables):
                return False
        return True

    def apply(self, rule):
        variables = {}
        if rule[0].match(self, variables):
            return rule[1].substitute(variables)

        result = deepcopy(self)
        for i in range(len(result.children)):
            applied = result.children[i].apply(rule)
            if applied is not None:
                result.children[i] = applied
                return result

        return None

    def substitute(self, variables):
        result = deepcopy(self)
        for i in range(len(result.children)):
            result.children[i] = result.children[i].substitute(variables)
        return result

    def rewrite(self, primary_rules, secondary_rules):
        state = self
        explored = set()
        print(state)
        while True:
            applied = False
            for rules in [primary_rules, secondary_rules]:
                for rule in rules:
                    result = state.apply(rule)
                    if result is not None and result not in explored:
                        state = result
                        explored.add(state)
                        applied = True
                        break
                if applied:
                    break
            if not applied:
                break
        return state

    def simplify(self):
        result = self.rewrite(EXPANSION_RULES, REARRANGEMENT_RULES)
        return result.rewrite(SIMPLIFICATION_RULES, REARRANGEMENT_RULES)


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
        return f"!{self.child}"


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


class And(Binary):
    def __init__(self, left, right):
        super().__init__(left, right, "*")


REARRANGEMENT_RULES = {
    # Commutative properties
    # a + b = b + a
    # a * b = b * a
    (Or(Variable("a"), Variable("b")), Or(Variable("b"), Variable("a"))),
    (And(Variable("a"), Variable("b")), And(Variable("b"), Variable("a"))),

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
    }

EXPANSION_RULES = {
    # Distributive property
    # a * (b + c) = (a * b) + (a * c)
    (And(Variable("a"), Or(Variable("b"), Variable("c"))),
     Or(And(Variable("a"), Variable("b")), And(Variable("a"), Variable("c")))),

    # De Morgan's laws
    # !(a + b) = !a * !b
    # !(a * b) = !a + !b
    (Not(Or(Variable("a"), Variable("b"))),
     And(Not(Variable("a")), Not(Variable("b")))),
    (Not(And(Variable("a"), Variable("b"))),
     Or(Not(Variable("a")), Not(Variable("b")))),
    }

SIMPLIFICATION_RULES = {
    # Inverse distributive property
    # (a * b) + (a * c) = a * (b + c)
    (Or(And(Variable("a"), Variable("b")), And(Variable("a"), Variable("c"))),
     And(Variable("a"), Or(Variable("b"), Variable("c")))),

    # a + a = a
    # a * a = a
    (Or(Variable("a"), Variable("a")), Variable("a")),
    (And(Variable("a"), Variable("a")), Variable("a")),

    # a + 0 = a
    # a + 1 = 1
    # a * 0 = 0
    # a * 1 = a
    (Or(Variable("a"), Constant(False)), Variable("a")),
    (Or(Variable("a"), Constant(True)), Constant(True)),
    (And(Variable("a"), Constant(False)), Constant(False)),
    (And(Variable("a"), Constant(True)), Variable("a")),

    # a + !a = 1
    # a * !a = 0
    (Or(Variable("a"), Not(Variable("a"))), Constant(True)),
    (And(Variable("a"), Not(Variable("a"))), Constant(False)),

    # a + (a * b) = a
    # a + (!a * b) = a + b
    # !a + (a * b) = !a + b
    (Or(Variable("a"), And(Variable("a"), Variable("b"))), Variable("a")),
    (Or(Variable("a"), And(Not(Variable("a")), Variable("b"))),
     Or(Variable("a"), Variable("b"))),
    (Or(Not(Variable("a")), And(Variable("a"), Variable("b"))),
     Or(Not(Variable("a")), Variable("b"))),

    # !!a = a
    # !0 = 1
    # !1 = 0
    (Not(Not(Variable("a"))), Variable("a")),
    (Not(Constant(False)), Constant(True)),
    (Not(Constant(True)), Constant(False)),
    }

expr = Or(And(Variable("a"), Variable("b")),
          And(And(Variable("b"), Variable("c")),
              Or(Variable("b"), Variable("c"))))

print(expr.simplify())
