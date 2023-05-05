# representation of https://www.allaboutcircuits.com/textbook/digital/chpt-7/circuit-simplification-examples/

# TODO: should operations be made binary?

circuit = {
    "op": "+", "operands": [
        { "op": "*", "operands": [ "a", "b" ] },
        {
            "op": "*", "operands": [
                "b",
                "c",
                { "op": "+", "operands": [ "b", "c" ] }
            ]
        }
    ]
}

ops = {
    "+": lambda a, b: a or b,
    "*": lambda a, b: a and b
}

def eval_circuit(circuit, inputs):
    if isinstance(circuit, str):
        return inputs[circuit]

    operands = []
    for operand in circuit["operands"]:
        operands.append(eval_circuit(operand, inputs))

    result = operands[0]
    for i in range(1, len(operands)):
        result = ops[circuit["op"]](result, operands[i])
    return result


def expression(circuit):
    if isinstance(circuit, str):
        return circuit

    result = "(" + expression(circuit["operands"][0])
    for i in range(1, len(circuit["operands"])):
        result += " " + circuit["op"] + " " + expression(circuit["operands"][i])
    result += ")"
    return result


def truth_table(circuit, inputs):
    inputs = {(i, False) for i in inputs}
    for i in range(2 ** len(inputs)):
        for j in range(len(inputs)):
            if inputs[len(inputs) - 1 - j] == True:
                inputs[len(inputs) - 1 - j] = False
            else:
                inputs[len(inputs) - 1 - j] = True
                break

        print()
        print(inputs)
        print(eval_circuit(circuit, inputs))



def simplify(circuit):
    raise NotImplementedError

print(eval_circuit(circuit, {"a": True, "b": False, "c": True}))
print(expression(circuit))
truth_table(circuit, [ "a", "b", "c" ])
