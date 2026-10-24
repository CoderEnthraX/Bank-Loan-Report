"""label model trades (A ok/extra, B ok/provable extra) and dump features. python3 -I feat.py ['{json}'] > feats.tsv"""
import sys, os, json, importlib.util
F = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'; X = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/xl'
sys.path.insert(0, F); sys.path.insert(0, X)
import gtscore
from engine2 import prepare
from engine import rma
from load_xl import load
inp = next((json.loads(x) for x in sys.argv[1:] if x.startswith('{')), {})
spec = importlib.util.spec_from_file_location('m', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kc.py')); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
tr, win = gtscore.load_gt(os.path.join(F, '..', 'gt', 'final'))
tr = [t for t in tr if not str(t.get('conf') or '').startswith('xl')]
for g in tr:
    if not gtscore.covered(win, g['sym'], g['fill']): win.append(dict(sym=g['sym'], a=g['fill'], b=g['fill']))
XB = {('CRUDE', '2026-10-12 13:40'), ('CRUDE', '2026-10-15 18:30'), ('CRUDE', '2026-10-15 21:35'), ('CRUDE', '2026-10-16 11:40'), ('CRUDE', '2026-10-16 19:00')}
XL = load()
syms = sorted({w['sym'] for w in win} | {'SENSEX', 'CRUDE'})
cols = None
for s in syms:
    P = prepare(s); T = P['T']; O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = rma(P['tr'], 14); idx = {t: i for i, t in enumerate(T)}
    A50 = rma(P['tr'], 50)
    trades = M.run(s, inp)
    gts = [g for g in tr if g['sym'] == s]
    xls = [(x, idx.get(x['date'] + ' ' + x['tin'])) for x in XL if x['sym'] == s]
    prev = None
    for m in trades:
        i = m['arm']; d = m['dir']; f = m['fill']
        lab = ''
        if gtscore.covered(win, s, T[f]):
            lab = 'okA' if any(g['d'] == d and g['fill'] == T[f] for g in gts) else 'XA'
        if s in ('SENSEX', 'CRUDE'):
            if any(x['d'] == d and fi is not None and abs(fi - f) <= 1 for x, fi in xls): lab = lab or 'okB'
            elif (s, T[i]) in XB: lab = 'XB'
        a = A[i]
        def lvl(n): return max(H[max(0,i-n):i]) if d > 0 else min(L[max(0,i-n):i])
        rng = H[i] - L[i]
        ft = dict(sym=s, arm=T[i], lab=lab or '-', res=m['res'],
                  brk10=d*(C[i]-lvl(10))/a, brk5=d*(C[i]-lvl(5))/a, brk20=d*(C[i]-lvl(20))/a, brk30=d*(C[i]-lvl(30))/a,
                  hbrk10=d*((H[i] if d>0 else L[i])-lvl(10))/a,
                  rng=rng/a, body=abs(C[i]-O[i])/rng*100, ext=((H[i]-C[i]) if d>0 else (C[i]-L[i]))/rng*100,
                  mom10=d*(C[i]-C[i-10])/a, mom5=d*(C[i]-C[i-5])/a, mom20=d*(C[i]-C[i-20])/a, momO10=d*(C[i]-O[i-9])/a,
                  cv=d*(C[i]-V[i])/a, ov=d*(O[i]-V[i])/a, vs3=d*(V[i]-V[i-3])/a*100, vs1=d*(V[i]-V[i-1])/a*100, vsmin=min(d*(V[i-k]-V[i-k-1]) for k in range(3))/a*100,
                  since=P['sinceStart'][i], ce=d*(C[i]-m['entry'])/a, el=d*(m['entry']-lvl(10))/a, wait=f-i,
                  atrr=a/(A50[i] or a), prevgap=(i-prev['exit']) if prev and prev['exit'] is not None else 999,
                  prevsame=int(bool(prev and prev['dir']==d)), prevres=prev['res'] if prev else 0,
                  hiAge=next((k for k in range(1, 11) if (H[i-k] if d>0 else L[i-k]) == lvl(10)), 0),
                  dayhi=d*(C[i]-(max(H[j] for j in range(i-P['sinceStart'][i], i)) if d>0 else min(L[j] for j in range(i-P['sinceStart'][i], i))))/a if P['sinceStart'][i] > 0 else 0,
                  pbar=d*(C[i-1]-O[i-1])/a, p2=d*(C[i-2]-O[i-2])/a)
        prev = m
        if cols is None: cols = list(ft); print('\t'.join(cols))
        print('\t'.join(f'{v:.3f}' if isinstance(v, float) else str(v) for v in ft.values()))
