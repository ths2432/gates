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
