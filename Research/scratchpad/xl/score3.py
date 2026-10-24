"""Score the student log on the NEW data: NIFTY rows vs NSEIX:NIFTY1! (GIFT Nifty), NATURAL GAS rows vs MCX NATURALGAS (Oct contract).
Usage: python3 -I score3.py [module.py] ['{json}'] [d]   (same matching rules as score2.py part B)"""
import sys, os, json, importlib.util
F = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, F); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_xl import load
from engine2 import prepare
from engine import rma
args = sys.argv[1:]
modp = next((a for a in args if a.endswith('.py')), os.path.join(F, 'pine_final.py'))
inp = next((json.loads(a) for a in args if a.startswith('{')), {})
det = 'd' in args
spec = importlib.util.spec_from_file_location('m', modp); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
DS = {'NIFTY': 'NSE_NIFTY1', 'NATGAS': 'MCX_NATURALGAS'}
# student typos found by matching prices/exits: NATGAS #3-#5 are 10-12 (logged 10-09), #2 filled 19:45 (logged 17:45)
FIX = {('NATGAS', 2): (None, '19:45'), ('NATGAS', 3): ('2026-10-12', None), ('NATGAS', 4): ('2026-10-12', None), ('NATGAS', 5): ('2026-10-12', None), ('NIFTY', 37): (None, '10:50')}
def _fx(x, ls):
    d, t = FIX.get((ls, x['n']), (None, None)); x = dict(x); x['date'] = d or x['date']; x['tin'] = t or x['tin']; return x
for ls, ds in DS.items():
    X = [_fx(x, ls) for x in load() if x['sym'] == ls]
    P = prepare(ds); T = P['T']; A = rma(P['tr'], 14); idx = {t: i for i, t in enumerate(T)}
    trades = M.run(ds, inp); tm = sok = 0; rows = []
    for x in X:
        f = idx.get(x['date'] + ' ' + x['tin'])
        best = None
        for m in trades:
            if m['dir'] == x['d'] and f is not None and abs(m['fill'] - f) <= 1:
                if best is None or abs(m['fill'] - f) < abs(best['fill'] - f): best = m
        if best is None:
            near = [m for m in trades if f is not None and abs(m['fill'] - f) <= 6]
            rows.append(('MISS', x['n'], x['date'], x['tin'], 'L' if x['d'] > 0 else 'S', f"log e{x['entry']} s{x['stop']}", 'nearby:', [(T[m['fill']][11:], 'L' if m['dir'] > 0 else 'S', round(m['entry'], 2)) for m in near])); continue
        tm += 1; a = A[best['arm']] or 1
        ok = abs(best['stop'] - x['stop']) <= 0.06 * a + (1.0 if ls == 'NIFTY' else 0.06)
        sok += ok
        rows.append(('OK  ' if ok else 'STOP', x['n'], x['date'], x['tin'], 'L' if x['d'] > 0 else 'S', f"log e{x['entry']} s{x['stop']} | model e{best['entry']:.2f} s{best['stop']:.2f} fill {T[best['fill']][11:]} ({(best['stop'] - x['stop']) / a:+.2f} ATR stop, {(best['entry'] - x['entry']) / a:+.2f} ATR entry)"))
    print(f'{ls} on {ds} ({len(X)}): time-matched {tm}, missed {len(X) - tm}, stop correct {sok}/{tm}')
    if det: [print('  ', *r) for r in rows]
