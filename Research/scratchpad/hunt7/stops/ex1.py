"""Step1: for every logged B trade matched by the model, simulate exits with logged / normal / half stops; compare with logged exit+maxTP."""
import sys, json, importlib.util
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit'); sys.path.insert(0, S+'/xl')
from load_xl import load
from engine2 import prepare
from engine import rma
mod = sys.argv[1]; inp = json.loads(sys.argv[2]); only = sys.argv[3:] 
spec = importlib.util.spec_from_file_location('m', mod); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
DS = {'NIFTY': 'NSE_NIFTY1', 'NATGAS': 'MCX_NATURALGAS', 'SENSEX': 'SENSEX', 'CRUDE': 'CRUDE'}
FIX = {('NATGAS', 2): (None, '19:45'), ('NATGAS', 3): ('2026-10-12', None), ('NATGAS', 4): ('2026-10-12', None), ('NATGAS', 5): ('2026-10-12', None), ('SENSEX',66):(None,'09:40')}
def sim(P, f, d, e, s):
    H, L, T = P['H'], P['L'], P['T']; r = d * (e - s); mx = 0
    if r <= 0: return 'bad', 0
    for i in range(f, min(f + 400, len(H))):
        if (L[i] <= s if d > 0 else H[i] >= s): return T[i][5:], mx
        fav = (H[i] - e) if d > 0 else (e - L[i])
        mx = max(mx, min(4, int(fav / r / 0.5 + 1e-9)))
        if mx >= 4: return T[i][5:], 4
    return 'open', mx
for ls, ds in DS.items():
    P = prepare(ds); T = P['T']; A = rma(P['tr'], 14); idx = {t: i for i, t in enumerate(T)}; O,H,L,C=P['O'],P['H'],P['L'],P['C']
    tr = M.run(ds, inp)
    for x in [x for x in load() if x['sym'] == ls]:
        d0, t0 = FIX.get((ls, x['n']), (None, None)); dt = (d0 or x['date']) + ' ' + (t0 or x['tin'])
        f = idx.get(dt); best = None
        for m in tr:
            if m['dir'] == x['d'] and f is not None and abs(m['fill'] - f) <= 1:
                if best is None or abs(m['fill'] - f) < abs(best['fill'] - f): best = m
        if best is None: print(f"{ls} #{x['n']} {dt} MISS"); continue
        j = best['arm']; a = A[j]; d = x['d']; e = best['entry']
        hyp = dict(log=(x['entry'], x['stop']), norm=(e, e - d*1.8*a), half=(e, min(e-0.9*a, L[j]) if d > 0 else max(e+0.9*a, H[j])))
        res = {k: sim(P, best['fill'], d, ee, s) for k, (ee, s) in hyp.items()}
        logsr = d*(x['entry']-x['stop'])/a
        cons = [k for k in ('norm','half') if res[k][0][6:] == x['tout'] and ('TP %d'%res[k][1] == x['maxtp'] or (res[k][1]==0 and x['maxtp']=='SL'))]
        tag = 'MODEL-TIGHT' if best['tight'] else 'model-norm'
        print(f"{ls} #{x['n']} {dt} {'L' if d>0 else 'S'} logSR {logsr:.2f} {tag} | log exit {x['tout']} {x['maxtp']} | " + '  '.join(f"{k}:{v[0][6:]} TP{v[1]}" for k, v in res.items()) + f"  consistent={cons}")
