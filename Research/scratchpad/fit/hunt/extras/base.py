import importlib.util
_spec = importlib.util.spec_from_file_location('rfp', '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence/rule_firstday_prevday.py')
_m = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)
stop_fn = _m.stop_fn
def arm_fn(P, i, d, ctx):
    return True
