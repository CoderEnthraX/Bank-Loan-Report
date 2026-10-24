import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open('fpfeat.py').read().split('rows = []')[0])
rows = []
for t in tr:
    if t['fill'] not in recover(t['sym'])['T'] or not t['entry']: continue
    rows.append(('TP', t['sym'], arm_of(t), t['d']))
rows += [('FP', s, a, d) for s, a, d in FP]
for lag in (1, 2, 3, 4, 5, 6, 8, 10, 12):
    tp = []; fp = []
    for kind, s, a, d in rows:
        P = recover(s); i = P['T'].index(a); V = P['V']
        k = P['sinceStart'][i]
        v = d * (V[i] - V[i - lag]) if k >= lag else 1e9
        (tp if kind == 'TP' else fp).append((v, s, a))
    tp.sort(); fp.sort()
    print(lag, 'TP<=0:', [(s, a[5:]) for v, s, a in tp if v <= 0], ' FP<=0:', [(s, a[5:]) for v, s, a in fp if v <= 0])
