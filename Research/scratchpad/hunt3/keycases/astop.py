"""A stop/entry accuracy: python3 -I astop.py ['{json}'] -> count of A exact trades whose stop differs > 0.06 ATR"""
import sys, os, json, importlib.util
F='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'; sys.path.insert(0,F)
import gtscore
from engine2 import prepare
from engine import rma
inp = next((json.loads(x) for x in sys.argv[1:] if x.startswith('{')), {})
spec = importlib.util.spec_from_file_location('m', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kc.py')); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
tr, win = gtscore.load_gt(os.path.join(F,'..','gt','final'))
n = bad = 0
for s in sorted({t['sym'] for t in tr}):
    P=prepare(s); T=P['T']; A=rma(P['tr'],14)
    for m in M.run(s, inp):
        g=next((g for g in tr if g['sym']==s and g['fill']==T[m['fill']] and g['d']==m['dir']), None)
        if g and g.get('stop'):
            n += 1; a = A[m['arm']]
            if abs(g['stop'] - m['stop']) > 0.06 * a: bad += 1; print('  STOPDIFF', s, T[m['fill']], f"gt {g['stop']} model {m['stop']:.6g} ({(m['stop']-g['stop'])/a:+.2f} ATR)")
print('A stops compared', n, 'off', bad)
