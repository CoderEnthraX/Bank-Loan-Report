"""Score engine2 configurations against the extracted ground truth (gt/*.json)."""
import json, os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine2 import prepare, run
ALIAS = {'GC1!': 'GC', 'GC1': 'GC', 'GOLD': 'GC', 'XAUUSD': 'GC', 'EURUSD': 'EURUSD', 'NASDAQ': 'NASDAQ', 'NAS100': 'NASDAQ', 'US100': 'NASDAQ',
         'US TECH 100': 'NASDAQ', 'US30': 'US30', 'DOW': 'US30', 'CRUDE': 'CRUDE', 'CRUDEOIL1!': 'CRUDE', 'CRUDEOIL': 'CRUDE', 'NIFTY': 'NIFTY',
         'NIFTY50': 'NIFTY', 'SENSEX': 'SENSEX', 'ETH': 'ETH', 'ETHUSD': 'ETH'}
def norm(s):
    s = (s or '').upper().strip()
    for k, v in ALIAS.items():
        if s == k or s.startswith(k): return v
    return s
import re
def tnorm(t):
    m = re.search(r'(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})', t or '')
    return f'{m.group(1)} {m.group(2)}' if m else None
def load_gt(path):
    trades, windows = [], []
    for f in sorted(glob.glob(os.path.join(path, '*.json'))):
        for g in (lambda x: x if isinstance(x, list) else [x])(json.load(open(f))):
            for w in g.get('windows', []):
                a, b = tnorm(w['first_bar']), tnorm(w['last_bar'])
                if a and b and '~' not in (w['first_bar'] + w['last_bar']) and '>' not in w['last_bar']:
                    windows.append(dict(sym=norm(w['symbol']), a=a, b=b, img=w.get('image')))
            for t in g.get('orig_trades', []):
                trades.append(dict(sym=norm(t['symbol']), d=1 if t['dir'] == 'long' else -1, fill=tnorm(t['fill_bar']),
                                   entry=t.get('entry_exact') or t.get('entry_measured'), stop=t.get('stop_measured'),
                                   conf=t.get('confidence'), out=t.get('outcome'), exit=tnorm(t.get('exit_bar'))))
    # de-duplicate trades reported by several images
    seen = {}; 
    for t in trades:
        k = (t['sym'], t['d'], t['fill'])
        if k not in seen: seen[k] = t
        else:
            for f in ('exit', 'out', 'entry', 'stop'):
                if not seen[k].get(f) or (f == 'out' and seen[k][f] == 'open'): seen[k][f] = t.get(f) or seen[k].get(f)
    return list(seen.values()), windows
def covered(windows, sym, t):
    return any(w['sym'] == sym and w['a'] <= t <= w['b'] for w in windows)
def score(cfg, trades, windows, detail=False, near=2):
    syms = sorted({w['sym'] for w in windows} | {t['sym'] for t in trades})
    res = dict(exact=0, near=0, miss=0, extra=0, entry_err=0.0, stop_err=0.0, n_px=0); rows = []
    for s in syms:
        P = prepare(s); T = P['T']; idx = {t: i for i, t in enumerate(T)}
        for g in [t for t in trades if t['sym'] == s]:
            if g['fill'] in idx and not covered(windows, s, g['fill']): windows.append(dict(sym=s, a=g['fill'], b=g['fill'], img='trade-only'))
        mine = [m for m in run(P, cfg) if covered(windows, s, T[m['fill']])]
        used = set()
        for g in [t for t in trades if t['sym'] == s]:
            gi = idx.get(g['fill'])
            if gi is None: rows.append(('nodata', s, g['fill'])); continue
            if not covered(windows, s, g['fill']): windows.append(dict(sym=s, a=g['fill'], b=g['fill'], img='trade-only'))
            best = None
            for k, m in enumerate(mine):
                if k in used or m['dir'] != g['d']: continue
                dd = abs(m['fill'] - gi)
                if dd <= near and (best is None or dd < best[0]): best = (dd, k, m)
            if best is None:
                res['miss'] += 1; rows.append(('MISS', s, g['fill'], 'L' if g['d'] > 0 else 'S')); continue
            used.add(best[1]); m = best[2]
            res['exact' if best[0] == 0 else 'near'] += 1
            atr = P[('atr', 14)][m['arm']] or 1
            if g['entry']: res['entry_err'] += abs(m['entry'] - g['entry']) / atr
            if g['stop']: res['stop_err'] += abs(m['stop'] - g['stop']) / atr; res['n_px'] += 1
            rows.append(('ok' if best[0] == 0 else f'off{m["fill"]-gi:+d}', s, g['fill'], 'L' if g['d'] > 0 else 'S',
                         f"entry {m['entry']:.6g}/{g['entry']}", f"stop {m['stop']:.6g}/{g['stop']}"))
        for k, m in enumerate(mine):
            if k not in used: res['extra'] += 1; rows.append(('EXTRA', s, T[m['fill']], 'L' if m['dir'] > 0 else 'S'))
    res['obj'] = 3 * res['exact'] + res['near'] - 2 * res['miss'] - 2 * res['extra']
    return (res, rows) if detail else res
if __name__ == '__main__':
    tr, win = load_gt(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'gt', 'final'))
    print(len(tr), 'trades', len(win), 'windows')
    r, rows = score({}, tr, win, detail=True)
    print(r); [print(' ', *x) for x in rows]
