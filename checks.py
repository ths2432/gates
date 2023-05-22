import check50
import check50.py

@check50.check()
def exists():
    """gates.py exists"""
    check50.exists("gates.py")

@check50.check(exists)
def cost_constant():
    """cost of a constant is 1"""
    g = check50.py.import_("gates.py")
    tests = [(g.Constant(True), 1), (g.Constant(False), 1)]
    for test in tests:
        if test[0].cost() != test[1]:
            raise check50.Failure()

@check50.check(exists)
def cost_variable():
    """cost of a variable is 1"""
    g = check50.py.import_("gates.py")
    if g.Variable("a").cost() != 1:
        raise check50.Failure()

@check50.check(exists)
def simplify1():
    """tests the simplification of an expression"""
    g = check50.py.import_("gates.py")
    expr = g.And(g.Or(g.Variable("a"), g.Variable("b")), g.Or(g.Variable("a"), g.Variable("d")))
    simplified = expr.simplify()
    if not simplified.equivalent(expr):
        raise check50.Failure()
    if simplified.cost() > 5:
        raise check50.Failure()

@check50.check(exists)
def simplify2():
    """tests the simplification of an expression"""
    g = check50.py.import_("gates.py")
    expr = g.Or(g.Or(g.Variable("a"), g.Variable("b")), g.Or(g.Variable("a"), g.Variable("b")))
    simplified = expr.simplify()
    if not simplified.equivalent(expr):
        raise check50.Failure()
    if simplified.cost() > 3:
        raise check50.Failure()

@check50.check(exists)
def simplify3():
    """tests the simplification of an expression"""
    g = check50.py.import_("gates.py")
    expr = g.Or(g.And(g.Variable("a"), g.Variable("b")),
          g.And(g.And(g.Variable("b"), g.Variable("c")), g.Or(g.Variable("b"), g.Variable("c"))))
    simplified = expr.simplify()
    if not simplified.equivalent(expr):
        raise check50.Failure()
    if simplified.cost() > 5:
        raise check50.Failure()

@check50.check(exists)
def simplify4():
    """tests the simplification of an expression"""
    g = check50.py.import_("gates.py")
    expr = g.Not(g.And(g.And(g.Not(g.Variable("a")), g.Variable("b")), g.Not(g.Variable("c"))))
    simplified = expr.simplify()
    if not simplified.equivalent(expr):
        raise check50.Failure()
    if simplified.cost() > 6:
        raise check50.Failure()

@check50.check(exists)
def simplify5():
    """tests the simplification of an expression"""
    g = check50.py.import_("gates.py")
    expr = g.Not(g.And(g.Not(g.And(g.Variable("a"), g.Variable("b"))), g.And(g.Not(g.Variable("c")), g.Variable("d"))))
    simplified = expr.simplify()
    if not simplified.equivalent(expr):
        raise check50.Failure()
    if simplified.cost() > 8:
        raise check50.Failure()