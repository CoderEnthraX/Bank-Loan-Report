import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
exec(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence/prevlvl.py').read().split("keys = sorted")[0])
for k in ('trS_stop', 'trS_entry', 'arm_ext', 'trO_t4'):
    print('==', k)
    for (s, f), (t, r) in sorted(res.items(), key=lambda x: x[1][1].get(k, 99)):
        v = r.get(k)
        if v is not None and v < 1.79: print(f"  {s:6s} {f} {'L' if t['d']>0 else 'S'} {'TIGHT' if t['tight'] else '     '} {v:7.2f}")
