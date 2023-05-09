from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, children):
        self.children = children

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def eval(self):
        pass


class Input(Node):
    def __init__(self, name, value):
        super().__init__([])
        self.name = name
        self.value = value

    def __str__(self):
        return self.name

    def eval(self):
        return self.value


class AndGate(Node):
    def __init__(self, children):
        super().__init__(children)

    def __str__(self):
        return f"{''.join([str(child) for child in self.children])}"

    def eval(self):
        value = True
        for child in self.children:
            value = value and child.eval()
        return value


class OrGate(Node):
    def __init__(self, children):
        super().__init__(children)

    def __str__(self):
        return f"({' + '.join([str(child) for child in self.children])})"

    def eval(self):
        value = False
        for child in self.children:
            value = value or child.eval()
        return value


def print_truth_table(circuit):
    # TODO
    pass
    

def simplify(circuit):
    # TODO
    pass


# terrible testing
# ab + bc(b + c)
a = Input("a", False)
b = Input("b", False)
c = Input("c", False)
ab = AndGate([ a, b ])
o = OrGate([ b, c ])
bc = AndGate([ b, c, o ])
o2 = OrGate([ ab, bc ])
print(o2)
