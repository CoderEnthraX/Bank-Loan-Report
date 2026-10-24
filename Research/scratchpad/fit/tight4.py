import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open('fpfeat.py').read().split('rows = []')[0])
X = []
for t in tr:
    P = recover(t['sym']); T = P['T']
    if t['fill'] not in T or not t['entry'] or not t['stop']: continue
    a = arm_of(t); i = T.index(a); d = t['d']; e = t['entry']
    A = P[('atr', 14)][i]
    tight = d * (e - t['stop']) / A < 1.5
    X.append((t['sym'], t['fill'], tight, 100 * A / e, P['mt']))
for s in sorted(set(x[0] for x in X)):
    print(s, ' '.join(('*' if x[2] else '') + '%.4f' % x[3] for x in sorted([x for x in X if x[0] == s], key=lambda x: x[3])))
