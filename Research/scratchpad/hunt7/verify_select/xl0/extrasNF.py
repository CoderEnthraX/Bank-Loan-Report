"""Provable extras in the student log B: model trades that could not have been taken by the original because the
original was inside a logged trade at that time (overlap), or that block a logged trade the model misses.
Usage: python3 -I extrasB.py [module.py] ['{json}']"""
import sys, os, json, importlib.util
F = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, F); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_xl import load
from engine2 import prepare
args = sys.argv[1:]
modp = next((a for a in args if a.endswith('.py')), os.path.join(F, 'pine_final.py'))
inp = next((json.loads(a) for a in args if a.startswith('{')), {})
spec = importlib.util.spec_from_file_location('m', modp); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
fixT = {66: '09:40'}
for sym in ('NSE_NIFTY1',):
    P = prepare(sym); T = P['T']; idx = {t: i for i, t in enumerate(T)}
    trades = M.run(sym, inp)
    X = [x for x in load() if x['sym'] == 'NIFTY']
    logged = []
    for x in X:
        f = idx.get(x['date'] + ' ' + fixT.get(x['n'], x['tin']))
        e = idx.get(x['date'] + ' ' + x['tout']) if x.get('tout') else None
        if f is not None: logged.append((x, f, e if e is not None and e >= f else f))
    days = sorted({x['date'] for x, _, _ in logged})
    for m in trades:
        if T[m['fill']][:10] not in days: continue
        matched = any(x['d'] == m['dir'] and abs(m['fill'] - f) <= 1 for x, f, e in logged)
        if matched: continue
        why = []
        for x, f, e in logged:
            if f < m['fill'] <= e: why.append(f"inside logged #{x['n']} {x['tin']}-{x['tout']}")
            mx = m['exit'] if m.get('exit') is not None else m['fill']
            if m['fill'] <= f <= mx + 2 and not any(mm['dir'] == x['d'] and abs(mm['fill'] - f) <= 1 for mm in trades):
                why.append(f"blocks logged #{x['n']} {x['tin']} {'L' if x['d']>0 else 'S'}")
        tag = 'PROVABLE-EXTRA' if why else 'unlogged'
        print(tag, sym, T[m['arm']], '->', T[m['fill']], 'L' if m['dir'] > 0 else 'S', m.get('res'), '|', '; '.join(why))
