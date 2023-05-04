class Gate:
    def __init__(self, func):
        self.func = func
        self.inputs = []

    def eval(self):
        inputs = []
        for input in self.inputs:
            inputs.append(input.eval())
        return self.func(inputs)


def buffer_gate(inputs):
    if len(inputs) != 1:
        raise ValueError

    return inputs[0]


def not_gate(inputs):
    if len(inputs) != 1:
        raise ValueError

    return not inputs[0]


def and_gate(inputs):
    output = True
    for input in inputs:
        output = output and input
    return output


def or_gate(inputs):
    output = False
    for input in inputs:
        output = output or input
    return output
    

def simplify(circuit):
    raise NotImplementedError


root = Gate(and_gate)
org = Gate(or_gate)
a = Gate(lambda inputs: True)
b = Gate(lambda inputs: True)
c = Gate(lambda inputs: False)
org.inputs = [ a, b ]
root.inputs = [ org, c ]
print(root.eval())
