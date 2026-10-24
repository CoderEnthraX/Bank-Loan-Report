"""In-process scorer replicating xl/score2.py; returns counts + identity sets."""
import sys, os, json, importlib.util
F = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
XL = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/xl'
sys.path.insert(0, F); sys.path.insert(0, XL); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_xl import load
from engine2 import prepare
from engine import rma
import gtscore, m as M
TR, WIN = gtscore.load_gt(os.path.join(F, '..', 'gt', 'final'))
TR = [t for t in TR if not str(t.get('conf') or '').startswith('xl')]
X = [x for x in load() if x['sym'] in ('SENSEX', 'CRUDE')]
fixT = {66: '09:40'}
PB = {s: prepare(s) for s in ('SENSEX', 'CRUDE')}
AB = {s: rma(PB[s]['tr'], 14) for s in PB}
def ev(inp):
    def _r(P, cfg):
        if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
        return M.run(P['sym'], inp)
    gtscore.run = _r
    ra, rowsA = gtscore.score({}, TR, [dict(w) for w in WIN], detail=True)
    Abad = {f'A{x[0]} {x[1]} {x[2]} {x[3]}' for x in rowsA if x[0] != 'ok'}
    tm = so = 0; Bmiss = set(); Bstop = set()
    for sym in ('SENSEX', 'CRUDE'):
        P = PB[sym]; T = P['T']; A = AB[sym]; idx = {t: i for i, t in enumerate(T)}
        trades = M.run(sym, inp)
        for x in [x for x in X if x['sym'] == sym]:
            f = idx.get(x['date'] + ' ' + fixT.get(x['n'], x['tin'])); best = None
            for t in trades:
                if t['dir'] == x['d'] and f is not None and abs(t['fill'] - f) <= 1:
                    if best is None or abs(t['fill'] - f) < abs(best['fill'] - f): best = t
            if best is None: Bmiss.add(f"B#{x['n']}"); continue
            tm += 1; a = A[best['arm']] or 1
            ok = abs(best['stop'] - x['stop']) <= 0.06 * a + 1.0; so += ok
            if not ok: Bstop.add(f"Bstop#{x['n']}")
    r = dict(Ae=ra['exact'], Am=ra['miss'], Ax=ra['extra'], Bm=tm, Bs=so)
    r['obj'] = tm + so + 3 * ra['exact'] - 2 * ra['miss'] - 2 * ra['extra']
    r['bad'] = Abad | Bmiss | Bstop
    return r
def fmt(r): return f"A {r['Ae']}/{r['Am']}/{r['Ax']}  B {r['Bm']} m {r['Bs']} s  obj {r['obj']}"
if __name__ == '__main__':
    r = ev(json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}); print(fmt(r)); print(sorted(r['bad']))
