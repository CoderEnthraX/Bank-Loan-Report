"""Shared research evaluator (accuracy research, separate from the clone work).
run_all(module_path, opts) -> labelled trades of every instrument; stats(trades) -> hit rates / expectancy; split by time.
Labels (stop-first, like the engine): mfeR = best favourable excursion in R before the stop (fill bar counts only for the stop),
hit06/hit1/hit15/hit2 = reached 0.6/1/1.5/2 R before the stop. E2 = engine result at the 2R exit (+2/-1);
E1 = +1 if hit1 else -1 (fixed 1R exit approximation), E15 = +1.5 if hit15 else -1."""
import sys, importlib.util, math, random
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fit')
from engine2 import prepare
from engine import rma
NEW = {"slopeCross": True, "minOpenBars": 0, "cooldownBars": 1, "dayStopR": 0, "tightOut": True, "erMin": 0.2}
SYMS = ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'NIFTY', 'SENSEX', 'ETH', 'NSE_NIFTY1', 'MCX_NATURALGAS']
SPLIT = '2026-10-01'          # TRAIN = fills before this date, TEST = from it (NSE_NIFTY1 / MCX_NATURALGAS are test-only)
_mods = {}
def load_module(path):
    if path not in _mods:
        spec = importlib.util.spec_from_file_location('m%d' % len(_mods), path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); _mods[path] = m
    return _mods[path]
def label(P, x):
    H, L = P['H'], P['L']; n = len(H); d = x['dir']; e = x['entry']; R = d * (e - x['stop']); f = x['fill']
    mfe = mae = 0.0; k = f
    while k < n:
        fav = d * ((H[k] if d > 0 else L[k]) - e) / R; adv = d * (e - (L[k] if d > 0 else H[k])) / R
        if adv >= 1.0 - 1e-9: break
        if k > f: mfe = max(mfe, fav)
        mae = max(mae, adv); k += 1
        if mfe >= 3.0: break
    return R, mfe, mae
def run_all(module_path=S + '/hunt4/combo.py', opts=None, syms=SYMS):
    M = load_module(module_path); o = dict(NEW); o.update(opts or {}); out = []
    for sym in syms:
        P = prepare(sym); T = P['T']; A = rma(P['tr'], 14)
        for x in M.run(sym, o):
            if x['exit'] is None: continue
            R, mfe, mae = label(P, x)
            out.append(dict(sym=sym, arm=x['arm'], fill=x['fill'], exit=x['exit'], t=T[x['fill']], dir=x['dir'], entry=x['entry'], stop=x['stop'],
                            R=R, atr=A[x['arm']], tight=bool(x.get('tight')), res=x['res'], mfe=mfe, mae=mae,
                            hit06=mfe >= 0.6, hit1=mfe >= 1.0, hit15=mfe >= 1.5, hit2=mfe >= 2.0))
    return out
def stats(tr):
    n = len(tr)
    if not n: return dict(n=0)
    E2 = sum(x['res'] for x in tr) / n; E1 = sum(1 if x['hit1'] else -1 for x in tr) / n; E15 = sum(1.5 if x['hit15'] else -1 for x in tr) / n
    gp = sum(x['res'] for x in tr if x['res'] > 0); gl = -sum(x['res'] for x in tr if x['res'] < 0)
    return dict(n=n, hit06=sum(x['hit06'] for x in tr) / n, hit1=sum(x['hit1'] for x in tr) / n, hit15=sum(x['hit15'] for x in tr) / n,
                hit2=sum(x['hit2'] for x in tr) / n, E1=E1, E15=E15, E2=E2, totR2=E2 * n, PF2=gp / gl if gl else float('inf'))
def split(tr): return [x for x in tr if x['t'] < SPLIT], [x for x in tr if x['t'] >= SPLIT]
def fmt(s):
    if not s['n']: return 'n=0'
    return (f"n={s['n']:4d} hit1R {s['hit1']:.1%} hit1.5R {s['hit15']:.1%} hit2R {s['hit2']:.1%} | E/trade 1R-exit {s['E1']:+.3f} 1.5R {s['E15']:+.3f} "
            f"2R {s['E2']:+.3f} | total2R {s['totR2']:+.0f} PF {s['PF2']:.2f}")
def boot_diff(a, b, key='res', it=2000, seed=1):
    """bootstrap CI of mean(key) difference b - a (a = baseline trades, b = filtered trades), returns (lo, hi)."""
    rnd = random.Random(seed); va = [x[key] if key == 'res' else x[key] for x in a]; vb = [x[key] for x in b]; ds = []
    for _ in range(it):
        sa = [va[rnd.randrange(len(va))] for _ in va]; sb = [vb[rnd.randrange(len(vb))] for _ in vb]; ds.append(sum(sb) / len(sb) - sum(sa) / len(sa))
    ds.sort(); return ds[int(0.025 * it)], ds[int(0.975 * it)]
def report(module_path=S + '/hunt4/combo.py', opts=None, base=None, per_sym=False):
    tr = run_all(module_path, opts); tn, te = split(tr)
    print('ALL  ', fmt(stats(tr))); print('TRAIN', fmt(stats(tn))); print('TEST ', fmt(stats(te)))
    if base is not None:
        bn, be = split(base)
        lo, hi = boot_diff(be, te); print(f'TEST E2 diff vs base {stats(te)["E2"] - stats(be)["E2"]:+.3f} R/trade, 95% CI [{lo:+.3f}, {hi:+.3f}]')
    if per_sym:
        for s in SYMS: print('  %-15s' % s, fmt(stats([x for x in tr if x['sym'] == s])))
    return tr
if __name__ == '__main__':
    import json
    opts = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    mod = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith('.py') else S + '/hunt4/combo.py'
    base = run_all() if opts else None
    report(mod, opts, base, per_sym=True)
