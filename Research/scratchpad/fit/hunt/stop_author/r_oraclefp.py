"""diagnostic only: wick-event rule with the 2 remaining static FPs forced normal (to measure the potential gain)."""
import os, json
os.environ['RULECFG'] = json.dumps({"ev": ["vsl", "wick"]})
import importlib.util
spec = importlib.util.spec_from_file_location('rpdx', '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author/r_pdx.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
EX = {('CRUDE', '2026-10-08 10:45'), ('NASDAQ', '2026-10-12 06:15')}
def stop_fn(P, i, d, entry, stop, A, ctx):
    if (P['sym'], P['T'][i]) in EX: return stop
    return m.stop_fn(P, i, d, entry, stop, A, ctx)
