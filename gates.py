from abc import ABC, abstractmethod
import itertools

class Node(ABC):
    def __init__(self, children):
        self.children = children

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return str(self)

    @abstractmethod
    def eval(self, inputs):
        pass

    def input_nodes(self):
        nodes = set()
        for child in self.children:
            if isinstance(child, Input):
                nodes.add(child)
            else:
                nodes = nodes.union(child.input_nodes())
        return nodes


class Input(Node):
    def __init__(self, name):
        super().__init__([])
        self.name = name

    def __str__(self):
        return self.name

    def eval(self, inputs):
        return inputs[self]


class AndGate(Node):
    def __init__(self, children):
        super().__init__(children)

    def __str__(self):
        return f"({' ∧ '.join([str(child) for child in self.children])})"

    def eval(self, inputs):
        value = True
        for child in self.children:
            value = value and child.eval(inputs)
        return value


class OrGate(Node):
    def __init__(self, children):
        super().__init__(children)

    def __str__(self):
        return f"({' ∨ '.join([str(child) for child in self.children])})"

    def eval(self, inputs):
        value = False
        for child in self.children:
            value = value or child.eval(inputs)
        return value


class NotGate(Node):
    def __init__(self, children):
        if len(children) != 1:
            raise ValueError("NotGate must have exactly one child")

        super().__init__(children)

    def __str__(self):
        return f"¬{str(self.children[0])}"

    def eval(self, inputs):
        return not self.children[0].eval(inputs)


# terrible testing
# ab + bc(b + c)
a = Input("a")
b = Input("b")
c = Input("c")
ab = AndGate([ a, b ])
o = OrGate([ b, c ])
bc = AndGate([ b, c, o ])
o2 = OrGate([ ab, bc ])
print(o2)
